"""Multi-agent chains for PBT - define and execute agent workflows"""

import yaml
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import networkx as nx


class ChainExecutionMode(Enum):
    """Execution modes for agent chains"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"


@dataclass
class AgentNode:
    """Node in an agent chain"""
    name: str
    prompt_file: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: List[str] = field(default_factory=list)
    conditions: Optional[Dict[str, Any]] = None
    retry_policy: Optional[Dict[str, Any]] = None
    
    
@dataclass
class ChainEdge:
    """Edge connecting agents in a chain"""
    source: str
    target: str
    condition: Optional[str] = None
    transform: Optional[str] = None


@dataclass
class ChainExecutionResult:
    """Result of chain execution"""
    chain_name: str
    success: bool
    outputs: Dict[str, Any]
    agent_results: Dict[str, Any]
    execution_path: List[str]
    errors: List[Dict[str, Any]] = field(default_factory=list)


class AgentChain:
    """Define and execute multi-agent workflows"""
    
    def __init__(self, chain_config: Union[str, Dict[str, Any]]):
        if isinstance(chain_config, str):
            # Load from file
            with open(chain_config, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = chain_config
            
        self.name = self.config.get('name', 'unnamed_chain')
        self.description = self.config.get('description', '')
        self.agents = self._load_agents()
        self.edges = self._load_edges()
        self.graph = self._build_graph()
        
    def _load_agents(self) -> Dict[str, AgentNode]:
        """Load agent definitions from config"""
        agents = {}
        for agent_config in self.config.get('agents', []):
            agent = AgentNode(
                name=agent_config['name'],
                prompt_file=agent_config['prompt_file'],
                inputs=agent_config.get('inputs', {}),
                outputs=agent_config.get('outputs', []),
                conditions=agent_config.get('conditions'),
                retry_policy=agent_config.get('retry_policy')
            )
            agents[agent.name] = agent
        return agents
    
    def _load_edges(self) -> List[ChainEdge]:
        """Load edge definitions from config"""
        edges = []
        for edge_config in self.config.get('flow', []):
            if isinstance(edge_config, dict):
                edge = ChainEdge(
                    source=edge_config['from'],
                    target=edge_config['to'],
                    condition=edge_config.get('condition'),
                    transform=edge_config.get('transform')
                )
            else:
                # Simple format: "agent1 -> agent2"
                parts = edge_config.split('->')
                if len(parts) == 2:
                    edge = ChainEdge(
                        source=parts[0].strip(),
                        target=parts[1].strip()
                    )
            edges.append(edge)
        return edges
    
    def _build_graph(self) -> nx.DiGraph:
        """Build directed graph of agent chain"""
        graph = nx.DiGraph()
        
        # Add nodes
        for agent_name, agent in self.agents.items():
            graph.add_node(agent_name, agent=agent)
        
        # Add edges
        for edge in self.edges:
            graph.add_edge(
                edge.source,
                edge.target,
                condition=edge.condition,
                transform=edge.transform
            )
        
        return graph
    
    def validate(self) -> Dict[str, Any]:
        """Validate the chain configuration"""
        issues = []
        warnings = []
        
        # Check for cycles
        if not nx.is_directed_acyclic_graph(self.graph):
            cycles = list(nx.simple_cycles(self.graph))
            issues.append(f"Chain contains cycles: {cycles}")
        
        # Check all agents have prompt files
        for agent_name, agent in self.agents.items():
            if not Path(agent.prompt_file).exists():
                issues.append(f"Agent '{agent_name}' prompt file not found: {agent.prompt_file}")
        
        # Check for disconnected agents
        if not nx.is_weakly_connected(self.graph):
            components = list(nx.weakly_connected_components(self.graph))
            warnings.append(f"Chain has disconnected components: {components}")
        
        # Check input/output compatibility
        for edge in self.edges:
            source_agent = self.agents.get(edge.source)
            target_agent = self.agents.get(edge.target)
            
            if source_agent and target_agent:
                source_outputs = set(source_agent.outputs)
                target_inputs = set(target_agent.inputs.keys())
                
                # Check if target needs inputs that source doesn't provide
                missing_inputs = target_inputs - source_outputs
                if missing_inputs and not edge.transform:
                    warnings.append(
                        f"Edge {edge.source}->{edge.target} may have missing inputs: {missing_inputs}"
                    )
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    def execute(
        self,
        initial_inputs: Dict[str, Any],
        runtime: Optional[Any] = None,
        max_iterations: int = 10
    ) -> ChainExecutionResult:
        """Execute the agent chain"""
        # Track execution state
        execution_state = {
            'completed': set(),
            'outputs': {},
            'agent_results': {},
            'execution_path': [],
            'errors': []
        }
        
        # Start with agents that have no dependencies
        start_nodes = [n for n in self.graph.nodes() if self.graph.in_degree(n) == 0]
        
        if not start_nodes:
            return ChainExecutionResult(
                chain_name=self.name,
                success=False,
                outputs={},
                agent_results={},
                execution_path=[],
                errors=[{'error': 'No start nodes found in chain'}]
            )
        
        # Execute chain
        success = self._execute_nodes(
            start_nodes,
            initial_inputs,
            execution_state,
            runtime,
            max_iterations
        )
        
        # Collect final outputs
        final_outputs = {}
        end_nodes = [n for n in self.graph.nodes() if self.graph.out_degree(n) == 0]
        for node in end_nodes:
            if node in execution_state['outputs']:
                final_outputs.update(execution_state['outputs'][node])
        
        return ChainExecutionResult(
            chain_name=self.name,
            success=success,
            outputs=final_outputs,
            agent_results=execution_state['agent_results'],
            execution_path=execution_state['execution_path'],
            errors=execution_state['errors']
        )
    
    def _execute_nodes(
        self,
        nodes: List[str],
        inputs: Dict[str, Any],
        state: Dict[str, Any],
        runtime: Optional[Any],
        max_iterations: int
    ) -> bool:
        """Execute a list of nodes"""
        iteration = 0
        pending = set(nodes)
        
        while pending and iteration < max_iterations:
            iteration += 1
            executed = set()
            
            for node in list(pending):
                # Check if dependencies are satisfied
                dependencies = list(self.graph.predecessors(node))
                if all(dep in state['completed'] for dep in dependencies):
                    # Gather inputs for this node
                    node_inputs = self._gather_node_inputs(node, inputs, state)
                    
                    # Execute agent
                    result = self._execute_agent(node, node_inputs, runtime)
                    
                    if result['success']:
                        state['outputs'][node] = result['outputs']
                        state['agent_results'][node] = result
                        state['completed'].add(node)
                        state['execution_path'].append(node)
                        executed.add(node)
                        
                        # Add successors to pending
                        successors = list(self.graph.successors(node))
                        for successor in successors:
                            # Check edge conditions
                            edge_data = self.graph.get_edge_data(node, successor)
                            if self._evaluate_condition(edge_data.get('condition'), result['outputs']):
                                pending.add(successor)
                    else:
                        state['errors'].append({
                            'agent': node,
                            'error': result.get('error', 'Unknown error')
                        })
                        # Handle retry policy
                        retry_policy = self.agents[node].retry_policy
                        if retry_policy and result.get('retry_count', 0) < retry_policy.get('max_retries', 3):
                            # Keep in pending for retry
                            result['retry_count'] = result.get('retry_count', 0) + 1
                        else:
                            executed.add(node)  # Give up on this node
            
            pending -= executed
            
            if not executed and pending:
                # No progress made - likely a dependency issue
                state['errors'].append({
                    'error': f'No progress made. Pending nodes: {pending}'
                })
                return False
        
        return len(state['errors']) == 0
    
    def _gather_node_inputs(
        self,
        node: str,
        initial_inputs: Dict[str, Any],
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gather inputs for a node from predecessors and initial inputs"""
        node_inputs = {}
        
        # Start with node's configured inputs
        agent = self.agents[node]
        node_inputs.update(agent.inputs)
        
        # Add initial inputs
        node_inputs.update(initial_inputs)
        
        # Gather outputs from predecessors
        for predecessor in self.graph.predecessors(node):
            if predecessor in state['outputs']:
                edge_data = self.graph.get_edge_data(predecessor, node)
                predecessor_outputs = state['outputs'][predecessor]
                
                # Apply transform if specified
                if edge_data and edge_data.get('transform'):
                    transformed = self._apply_transform(
                        predecessor_outputs,
                        edge_data['transform']
                    )
                    node_inputs.update(transformed)
                else:
                    node_inputs.update(predecessor_outputs)
        
        return node_inputs
    
    def _execute_agent(
        self,
        node: str,
        inputs: Dict[str, Any],
        runtime: Optional[Any]
    ) -> Dict[str, Any]:
        """Execute a single agent"""
        agent = self.agents[node]
        
        try:
            if runtime:
                # Use provided runtime
                outputs = runtime.execute_prompt(agent.prompt_file, inputs)
            else:
                # Mock execution for testing
                outputs = {
                    output_name: f"Mock output for {output_name}"
                    for output_name in agent.outputs
                }
            
            return {
                'success': True,
                'outputs': outputs,
                'agent': node,
                'inputs': inputs
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'agent': node,
                'inputs': inputs
            }
    
    def _evaluate_condition(self, condition: Optional[str], context: Dict[str, Any]) -> bool:
        """Evaluate edge condition"""
        if not condition:
            return True
        
        try:
            # Simple evaluation - in production use safe eval
            # For now, support basic comparisons
            if '>' in condition:
                parts = condition.split('>')
                left = context.get(parts[0].strip(), 0)
                right = float(parts[1].strip())
                return float(left) > right
            elif '<' in condition:
                parts = condition.split('<')
                left = context.get(parts[0].strip(), 0)
                right = float(parts[1].strip())
                return float(left) < right
            elif '==' in condition:
                parts = condition.split('==')
                left = context.get(parts[0].strip(), '')
                right = parts[1].strip().strip('"\'')
                return str(left) == right
            else:
                # Check if value is truthy
                return bool(context.get(condition, False))
        except:
            return True  # Default to true on error
    
    def _apply_transform(self, data: Dict[str, Any], transform: str) -> Dict[str, Any]:
        """Apply transformation to data"""
        # Simple transformations - extend as needed
        if transform == "flatten":
            # Flatten nested structure
            flattened = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        flattened[f"{key}_{sub_key}"] = sub_value
                else:
                    flattened[key] = value
            return flattened
        elif transform == "summarize":
            # Combine all values into summary
            return {"summary": " ".join(str(v) for v in data.values())}
        else:
            # No transform
            return data
    
    def visualize(self) -> str:
        """Generate Mermaid diagram of the chain"""
        lines = ["graph TD"]
        
        # Add nodes
        for node in self.graph.nodes():
            agent = self.agents[node]
            lines.append(f"    {node}[{node}<br/>{agent.prompt_file}]")
        
        # Add edges
        for source, target, data in self.graph.edges(data=True):
            label = ""
            if data.get('condition'):
                label = f"|{data['condition']}|"
            lines.append(f"    {source} -->{label} {target}")
        
        return "\n".join(lines)
    
    def to_yaml(self) -> str:
        """Export chain configuration to YAML"""
        config = {
            'name': self.name,
            'description': self.description,
            'agents': [
                {
                    'name': agent.name,
                    'prompt_file': agent.prompt_file,
                    'inputs': agent.inputs,
                    'outputs': agent.outputs,
                    'conditions': agent.conditions,
                    'retry_policy': agent.retry_policy
                }
                for agent in self.agents.values()
            ],
            'flow': [
                {
                    'from': edge.source,
                    'to': edge.target,
                    'condition': edge.condition,
                    'transform': edge.transform
                }
                for edge in self.edges
            ]
        }
        return yaml.dump(config, default_flow_style=False)


def create_chain_from_template(template: str) -> AgentChain:
    """Create a chain from a predefined template"""
    templates = {
        'summarize_critique_rewrite': {
            'name': 'Summarize-Critique-Rewrite',
            'description': 'Summarize content, critique it, then rewrite based on critique',
            'agents': [
                {
                    'name': 'summarizer',
                    'prompt_file': 'agents/summarizer.prompt.yaml',
                    'inputs': {'content': 'string'},
                    'outputs': ['summary']
                },
                {
                    'name': 'critic',
                    'prompt_file': 'agents/critic.prompt.yaml',
                    'inputs': {'content': 'string'},
                    'outputs': ['critique', 'score']
                },
                {
                    'name': 'rewriter',
                    'prompt_file': 'agents/rewriter.prompt.yaml',
                    'inputs': {'content': 'string', 'feedback': 'string'},
                    'outputs': ['improved_content']
                }
            ],
            'flow': [
                {'from': 'summarizer', 'to': 'critic'},
                {'from': 'critic', 'to': 'rewriter', 'condition': 'score < 8'}
            ]
        },
        'rag_pipeline': {
            'name': 'RAG-Pipeline',
            'description': 'Retrieve, augment, and generate response',
            'agents': [
                {
                    'name': 'retriever',
                    'prompt_file': 'agents/retriever.prompt.yaml',
                    'inputs': {'query': 'string'},
                    'outputs': ['documents', 'relevance_scores']
                },
                {
                    'name': 'augmenter',
                    'prompt_file': 'agents/augmenter.prompt.yaml',
                    'inputs': {'query': 'string', 'documents': 'list'},
                    'outputs': ['augmented_context']
                },
                {
                    'name': 'generator',
                    'prompt_file': 'agents/generator.prompt.yaml',
                    'inputs': {'query': 'string', 'context': 'string'},
                    'outputs': ['response']
                }
            ],
            'flow': [
                'retriever -> augmenter',
                'augmenter -> generator'
            ]
        }
    }
    
    if template not in templates:
        raise ValueError(f"Unknown template: {template}. Available: {list(templates.keys())}")
    
    return AgentChain(templates[template])