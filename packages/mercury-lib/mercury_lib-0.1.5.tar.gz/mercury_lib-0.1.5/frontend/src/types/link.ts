import { SimulationLinkDatum } from "d3"
import { type Node } from './node'

export type Link = SimulationLinkDatum<Node> & {
  label: string
}
