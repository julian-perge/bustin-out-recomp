//Exports the .text block of the current program as one COFF relocatable object.
//@category Project

import java.io.File;
import java.util.ArrayList;
import java.util.List;

import ghidra.app.plugin.core.analysis.AutoAnalysisManager;
import ghidra.app.script.GhidraScript;
import ghidra.app.services.Analyzer;
import ghidra.app.util.exporter.Exporter;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import ghidra.util.classfinder.ClassSearcher;

public class ExportTextObject extends GhidraScript {
	@Override
	public void run() throws Exception {
		File out = new File(getScriptArgs()[0]);
		MemoryBlock text = currentProgram.getMemory().getBlock(".text");
		AddressSet set = new AddressSet(text.getStart(), text.getEnd());

		println("thunks made ordinary functions: " + unthunk());
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
}
