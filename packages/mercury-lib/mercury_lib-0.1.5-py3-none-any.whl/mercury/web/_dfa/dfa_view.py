from pathlib import Path

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from mercury.automata import DeterministicFiniteAutomata as DFA

from .._dfa.dfa_schema import DFASchema, to_node, to_schema

# Cannot easily modify unless recompiling the frontend

# TODO: Review what options there are for frontend to
# dynamically find the backend's port
PORT = 8081


class DFAView:

    _automata: DFA
    _app: FastAPI
    _router: APIRouter

    def __init__(self, automata: DFA) -> None:
        self._automata = automata
        self._app = FastAPI(
            title="Mercury API Interface",
            description="Mercury API made in order to link the library to a web interface",
        )
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allow all origins (for dev)
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self._router = APIRouter()
        self._register_routes()

        static_dir = Path(__file__).parent.parent.parent / "static"
        self._app.mount(
            "/view", StaticFiles(directory=static_dir, html=True), name="spa"
        )
        self._app.include_router(self._router, prefix="/api")

    def _register_routes(self):

        @self._router.get("/automata")
        async def fetch_automata() -> DFASchema:
            "Returns basic information about the automata that is currently running"
            return to_schema(self._automata)

        @self._router.post("/automata/execute")
        async def execute_automata(input_string: str):
            "Executes the input string on the DFA at once, returning the states it went through"
            states = list(self._automata.read_input_stepwise(input_string))
            return {
                "nodes": [to_node(state) for state in states],
                "accepted": states[-1] in self._automata.final_states,
            }

    def run(self, host: str = "0.0.0.0"):
        """Run the FastAPI application using uvicorn"""
        print("Graphical automata view can be seen at http://127.0.0.1:8081/view")
        uvicorn.run(self._app, host=host, port=PORT, log_level="critical")
