import { Automata } from "../types/automata";
import { Link } from "../types/link";

// Since we get duplicate links from the raw automata in the library,
// we process them here to fuse their labels
export function processTransitions(automata: Automata) {
  const newAutomata = structuredClone(automata);
  const newLinks: Link[] = [];

  automata.links.forEach((link) => {
    const repeatedLink = newLinks.find(
      (newLink) =>
        newLink.target == link.target && newLink.source == link.source,
    );
    if (repeatedLink) {
      repeatedLink.label = `${repeatedLink.label}, ${link.label}`;
    } else {
      newLinks.push(link);
    }
  });

  newAutomata.links = newLinks;
  return newAutomata;
}
