from typing import Literal

from pydantic import BaseModel

from mercury.automata import DeterministicFiniteAutomata
from mercury.types import State


class DFANode(BaseModel):
    id: str
    label: str


class DFALink(BaseModel):
    label: str
    source: str
    target: str


class DFASchema(BaseModel):
    nodes: list[DFANode]
    links: list[DFALink]
    initial_node: DFANode
    final_nodes: list[DFANode]


class DFAEndResult(BaseModel):
    accepted: bool


class DFAStepResult(BaseModel):
    status: Literal["ongoing", "finished"]
    result: DFANode | bool


def to_schema(dfa: DeterministicFiniteAutomata) -> DFASchema:
    nodes: list[DFANode] = []
    links: list[DFALink] = []
    for state in dfa.states:
        nodes.append(to_node(state))
    for initial_conditions, next_state in dfa.transitions.items():
        links.append(
            DFALink(
                label=initial_conditions[1],
                source=str(initial_conditions[0]),
                target=str(next_state),
            )
        )
    return DFASchema(
        nodes=nodes,
        links=links,
        initial_node=DFANode(
            id=str(dfa.initial_state),
            label="".join([str(cmp) for cmp in dfa.initial_state]),
        ),
        final_nodes=[
            DFANode(
                id=str(state),
                label="".join([str(cmp) for cmp in state]),
            )
            for state in dfa.final_states
        ],
    )


def to_node(state: State) -> DFANode:
    return DFANode(label="".join([str(cmp) for cmp in state]), id=str(state))
