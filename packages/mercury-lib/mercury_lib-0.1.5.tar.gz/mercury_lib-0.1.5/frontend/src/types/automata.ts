import { Link } from './link';
import { Node } from './node'

export type Automata = {
  nodes: Node[];
  links: Link[];
  initial_node: Node;
  final_nodes: Node[];
}
