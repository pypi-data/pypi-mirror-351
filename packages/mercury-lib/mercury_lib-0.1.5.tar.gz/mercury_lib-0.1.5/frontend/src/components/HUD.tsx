import { FastForward, Play, RotateCcw, StepForward } from "lucide-react";
import { useEffect, useState } from "react";

type HUDProps = {
  onPlay: (input_string: string) => void;
  onNextStep: (input_string: string) => void;
  onFastForward: (input_string: string) => void;
  onReset: () => void;
  onChangeInputString: () => void;
  onChangeDelay: (delay: number) => void;
};

export default function HUD({
  onPlay,
  onNextStep,
  onFastForward,
  onReset,
  onChangeInputString,
  onChangeDelay,
}: HUDProps) {
  const [inputString, setInputString] = useState<string>("");
  const [stringDelay, setStringDelay] = useState<string>("1.0");
  const [delay, setDelay] = useState<number>(1);

  const handleChangeStringDelay = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const input = event.target.value;

    if (/^\d*\.?\d*$/.test(input)) {
      setStringDelay(input);

      if (!isNaN(Number(input))) {
        setDelay(Number(input));
      }
    }
  };

  const changeDelay = (delta: number) => {
    setDelay((oldDelay) => {
      const newDelay = +Math.max(oldDelay + delta, 0.05).toFixed(2);
      setStringDelay(
        Number.isInteger(newDelay) ? `${newDelay}.0` : newDelay.toString(),
      );
      return newDelay;
    });
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === "Enter") {
      onPlay(inputString);
    }
  };

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    onChangeInputString(); // Reset execution
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [inputString]);

  useEffect(() => {
    onChangeDelay(delay);
  }, [delay]);

  return (
    <div className="absolute z-10 flex flex-col w-full h-full justify-between pointer-events-none">
      <div className="flex justify-between">
        <a href="#" className="pointer-events-auto">
          <img
            src="pyGold.svg"
            className="h-16 px-4 py-2 m-4 bg-gray-100 rounded-2xl"
            alt="Mercury Logo"
          />
        </a>
        <div className="flex items-center">
          <input
            type="text"
            className="bg-gray-100 text-gray-700 tracking-widest font-mono rounded-2xl w-80 h-16 m-4 px-8 pointer-events-auto"
            placeholder="Enter input..."
            value={inputString}
            onChange={(e) => setInputString(e.target.value)}
          />
          <button
            className="flex items-center justify-center bg-gray-100 rounded-2xl w-16 h-16 mr-4 px-8 pointer-events-auto hover:cursor-pointer"
            onClick={() => onNextStep(inputString)}
          >
            <StepForward className="min-w-12 text-gray-600" />
          </button>
          <button
            className="flex items-center justify-center bg-gray-100 rounded-2xl w-16 h-16 mr-4 pointer-events-auto hover:cursor-pointer"
            onClick={() => onPlay(inputString)}
          >
            <Play className="min-w-12 text-gray-600" />
          </button>
          <button
            className="flex items-center justify-center bg-gray-100 rounded-2xl w-16 h-16 mr-4 pointer-events-auto hover:cursor-pointer"
            onClick={() => onFastForward(inputString)}
          >
            <FastForward className="min-w-12 text-gray-600" />
          </button>
          <button
            className="flex items-center justify-center bg-gray-100 rounded-2xl w-16 h-16 mr-4 pointer-events-auto hover:cursor-pointer"
            onClick={() => onReset()}
          >
            <RotateCcw className="min-w-12 text-gray-600" />
          </button>
        </div>
      </div>
      <div className="flex justify-between">
        <div className="flex p-4 m-4">
          <button
            className="bg-gray-100 pointer-events-auto size-8"
            onClick={() => changeDelay(0.05)}
          >
            +
          </button>
          <input
            type="text"
            inputMode="decimal"
            className=" bg-gray-100 w-16 pointer-events-auto ml-4 mr-1 font-mono rounded text-center"
            value={stringDelay}
            onChange={handleChangeStringDelay}
          />
          <span className="text-center font-mono align-baseline italic mr-2 mt-1">
            s
          </span>
          <button
            className="bg-gray-100 pointer-events-auto size-8"
            onClick={() => changeDelay(-0.05)}
          >
            -
          </button>
        </div>
      </div>
    </div>
  );
}
