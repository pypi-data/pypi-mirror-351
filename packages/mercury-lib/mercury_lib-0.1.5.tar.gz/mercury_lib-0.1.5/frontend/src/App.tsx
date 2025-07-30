import { useState, useEffect, useRef } from "react";
import Graph from "./components/Graph";
import { Automata } from "./types/automata";
import { Node } from "./types/node";

import HUD from "./components/HUD";
import axios from "axios";
import { Execution } from "./types/execution";
import { processTransitions } from "./lib/automata";

const BACKEND_URL = "http://localhost:8081/api";

export default function App() {
  const [automata, setAutomata] = useState<Automata | null>(null);
  const [currentExecution, setCurrentExecution] = useState<Execution | null>(
    null,
  );

  // Set highlights, regular = yellow, error = red, success = green
  const [highlightedNodes, setHighlighedNodes] = useState<Node[]>([]);
  const [highlightedErrorNodes, setHighlighedErrorNodes] = useState<Node[]>([]);
  const [highlightedSuccessNodes, setHighlighedSuccessNodes] = useState<Node[]>(
    [],
  );

  // Delay per step in seconds
  const [stepDelay, setStepDelay] = useState<number>(1);

  // Current step of the execution
  const [currentStep, setCurrentStep] = useState<number | null>(null);

  // Checks if the execution is running, i.e, if the play state is on
  const [executionRunning, setExecutionRunning] = useState(false);

  // Play state interval
  const intervalRef = useRef<number | null>(null);

  const fetchAutomata = async () => {
    try {
      const automataResponse = (
        await axios.get<Automata>(`${BACKEND_URL}/automata`)
      ).data;
      const processedAutomata = processTransitions(automataResponse);
      setAutomata(processedAutomata);
    } catch (err) {
      console.error("Failed to fetch automata:", err);
    }
  };

  const playAutomata = async (input_string: string) => {
    if (!currentExecution) {
      await fetchExecution(input_string);
    } else {
      setCurrentStep((currentStep) =>
        currentStep !== null
          ? Math.min(currentStep + 1, currentExecution.nodes.length - 1)
          : null,
      );
    }
    setExecutionRunning(true);
  };

  const nextStepAutomata = async (input_string: string) => {
    if (currentExecution) {
      setCurrentStep((currentStep) =>
        currentStep !== null
          ? Math.min(currentStep + 1, currentExecution.nodes.length - 1)
          : null,
      );
      setExecutionRunning(false);
    } else {
      await fetchExecution(input_string);
    }
  };

  const fastForwardAutomata = async (input_string: string) => {
    let newExecution: Execution | null = null;
    if (!currentExecution) {
      newExecution = await fetchExecution(input_string);
    }
    setCurrentStep((currentStep) =>
      currentStep !== null
        ? (currentExecution ? currentExecution : newExecution!).nodes.length
        : null,
    );
  };

  const fetchExecution = async (input_string: string) => {
    const executionResponse = (
      await axios.post<Execution>(
        `${BACKEND_URL}/automata/execute`,
        {},
        {
          params: {
            input_string: input_string,
          },
        },
      )
    ).data;
    setCurrentExecution(executionResponse);
    setCurrentStep(0);
    return executionResponse;
  };

  const clearAllHighlightedNodes = () => {
    setHighlighedNodes([]);
    setHighlighedSuccessNodes([]);
    setHighlighedErrorNodes([]);
  };

  const resetExecution = () => {
    setCurrentExecution(null);
    setCurrentStep(null);
    clearAllHighlightedNodes();
  };

  useEffect(() => {
    fetchAutomata();
  }, []);

  useEffect(() => {
    if (currentStep === null || currentExecution === null) return;

    clearAllHighlightedNodes();

    setTimeout(() => {
      if (currentStep >= currentExecution.nodes.length - 1) {
        const lastNode =
          currentExecution.nodes[currentExecution.nodes.length - 1];

        if (currentExecution.accepted) {
          setHighlighedSuccessNodes([lastNode]);
        } else {
          setHighlighedErrorNodes([lastNode]);
        }
        return;
      }

      setHighlighedNodes([currentExecution.nodes[currentStep]]);
    }, 150 * stepDelay);
  }, [currentStep, currentExecution]);

  useEffect(() => {
    if (executionRunning && currentExecution) {
      intervalRef.current = window.setInterval(() => {
        setCurrentStep((currentStep) =>
          currentStep !== null
            ? Math.min(currentStep + 1, currentExecution.nodes.length - 1)
            : null,
        );
      }, 1000 * stepDelay);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [executionRunning, currentExecution, stepDelay]);

  return (
    <div className="relative w-screen h-screen">
      {automata && (
        <Graph
          nodes={automata.nodes}
          links={automata.links}
          initialNode={automata.initial_node}
          finalNodes={automata.final_nodes}
          highlightedNodes={highlightedNodes}
          highlightedSuccessNodes={highlightedSuccessNodes}
          highlightedErrorNodes={highlightedErrorNodes}
        />
      )}
      <HUD
        onPlay={playAutomata}
        onNextStep={nextStepAutomata}
        onFastForward={fastForwardAutomata}
        onReset={resetExecution}
        onChangeInputString={resetExecution}
        onChangeDelay={(newDelay) => setStepDelay(newDelay)}
      />
    </div>
  );
}
