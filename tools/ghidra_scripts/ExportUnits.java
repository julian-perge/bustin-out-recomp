//Exports each unit listed in a units file (start and end address, hex, one pair
//per line) as its own COFF relocatable object named <start>.obj. Arguments: the
//units file, the output folder, and optionally how many units to export, for trials.
//tools/delink.sh no longer runs it, because it takes over an hour; it stays as the
//reference that bodecomp.unitsplit --compare checks the Python split against
//after a delinker update.
//@category Project

import java.io.File;
import java.nio.file.Files;
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

public class ExportUnits extends GhidraScript {
	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		List<String> lines = Files.readAllLines(new File(args[0]).toPath());
		File outDir = new File(args[1]);
		int limit = args.length > 2 ? Integer.parseInt(args[2]) : lines.size();
		outDir.mkdirs();

		println("thunks made ordinary functions: " + unthunk());
		println("mangled labels removed: " + removeMangledTies());
		MemoryBlock text = currentProgram.getMemory().getBlock(".text");
		AutoAnalysisManager manager = AutoAnalysisManager.getAnalysisManager(currentProgram);
		Analyzer synthesizer = manager.getAnalyzer("Relocation table synthesizer");
		manager.scheduleOneTimeAnalysis(synthesizer, new AddressSet(text.getStart(), text.getEnd()));
		manager.waitForAnalysis(null, monitor);

		Exporter exporter = ClassSearcher.getInstances(Exporter.class).stream()
			.filter(e -> e.getName().equals("COFF relocatable object"))
			.findFirst()
			.orElseThrow();
		exporter.setOptions(exporter.getOptions(() -> currentProgram));

		int written = 0;
		int failed = 0;
		for (String line : lines.subList(0, Math.min(limit, lines.size()))) {
			String[] parts = line.trim().split("\\s+");
			Address start = toAddr(Long.parseLong(parts[0], 16));
			Address last = toAddr(Long.parseLong(parts[1], 16) - 1);
			File out = new File(outDir, parts[0] + ".obj");
			exporter.getMessageLog().clear();
			if (exporter.export(out, currentProgram, new AddressSet(start, last), monitor)) {
				written++;
			}
			else {
				failed++;
				if (failed <= 20) {
					println("FAILED " + parts[0] + ": " + exporter.getMessageLog());
				}
			}
		}
		println("units written " + written + ", failed " + failed);
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
