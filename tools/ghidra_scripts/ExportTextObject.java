//Exports the .text block of the current program as one COFF relocatable object.
//@category Project

import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import ghidra.app.plugin.core.analysis.AutoAnalysisManager;
import ghidra.app.script.GhidraScript;
import ghidra.app.services.Analyzer;
import ghidra.app.util.exporter.Exporter;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.util.classfinder.ClassSearcher;

public class ExportTextObject extends GhidraScript {
	@Override
	public void run() throws Exception {
		File out = new File(getScriptArgs()[0]);
		MemoryBlock text = currentProgram.getMemory().getBlock(".text");
		AddressSet set = new AddressSet(text.getStart(), text.getEnd());

		println("thunks made ordinary functions: " + unthunk());
		println("mangled labels removed: " + removeMangledTies());
		AutoAnalysisManager manager = AutoAnalysisManager.getAnalysisManager(currentProgram);
		Analyzer synthesizer = manager.getAnalyzer("Relocation table synthesizer");
		manager.scheduleOneTimeAnalysis(synthesizer, set);
		manager.waitForAnalysis(null, monitor);

		Exporter exporter = ClassSearcher.getInstances(Exporter.class).stream()
			.filter(e -> e.getName().equals("COFF relocatable object"))
			.findFirst()
			.orElseThrow();
		exporter.setOptions(exporter.getOptions(() -> currentProgram));
		if (!exporter.export(out, currentProgram, set, monitor)) {
			throw new RuntimeException("COFF export failed: " + exporter.getMessageLog());
		}
		println("wrote " + out);
	}

	// The delinker names a call to a thunk after the thunk's target, so the
	// relinked call would skip the thunk. Making every thunk an ordinary
	// function, under its current name, keeps calls pointed at the thunk. The
	// project is opened read-only, so this change is never saved.
	private int unthunk() throws Exception {
		List<Function> thunks = new ArrayList<>();
		for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
			if (f.isThunk() && !f.isExternal()) {
				thunks.add(f);
			}
		}
		for (Function f : thunks) {
			String name = f.getName();
			f.setThunkedFunction(null);
			if (!f.getName().equals(name)) {
				f.setName(name, SourceType.ANALYSIS);
			}
		}
		return thunks.size();
	}

	// Function ID can leave the same mangled names as labels on two equal
	// functions, as on 0x0021E425 and 0x0021E42C. The exporter takes any one of
	// the mangled names at an address, so its choice changes with the symbol IDs
	// of the project, and both functions can get the same name, which stops the
	// export. Removing the labels with a mangled name that are not primary, at
	// each address that holds more than one, leaves the exporter the primary
	// name, which comes from config/symbols.txt. The project is opened
	// read-only, so this change is never saved.
	private int removeMangledTies() throws Exception {
		Map<Address, List<Symbol>> mangled = new HashMap<>();
		for (Symbol s : currentProgram.getSymbolTable().getAllSymbols(true)) {
			if (s.getAddress().isMemoryAddress() && s.getName(true).startsWith("?")) {
				mangled.computeIfAbsent(s.getAddress(), a -> new ArrayList<>()).add(s);
			}
		}
		int removed = 0;
		for (List<Symbol> symbols : mangled.values()) {
			if (symbols.size() < 2) {
				continue;
			}
			for (Symbol s : symbols) {
				if (!s.isPrimary()) {
					s.delete();
					removed++;
				}
			}
		}
		return removed;
	}
}
