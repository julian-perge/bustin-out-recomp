//Writes the delinker's relocations in .text and the symbol it would name at every
//address, so that bodecomp.unitsplit can cut the unit objects without one Ghidra
//export per unit. Arguments: the relocations file and the symbols file. Run it
//after ExportTextObject.java in the same session, which turns thunks into
//ordinary functions first.
//@category Project

import java.io.PrintWriter;
import java.util.Iterator;
import java.util.Map;
import java.util.StringJoiner;
import java.util.TreeMap;
import java.util.function.Predicate;
import java.util.stream.StreamSupport;

import ghidra.app.plugin.core.analysis.AutoAnalysisManager;
import ghidra.app.script.GhidraScript;
import ghidra.app.services.Analyzer;
import ghidra.app.util.SymbolInformation;
import ghidra.app.util.SymbolInformationCollector;
import ghidra.app.util.SymbolPreference;
import ghidra.app.util.predicates.visibility.IsSymbolDynamic;
import ghidra.app.util.predicates.visibility.IsSymbolInsideFunction;
import ghidra.app.util.predicates.visibility.IsSymbolNameMatchingRegex;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.relocobj.Relocation;
import ghidra.program.model.relocobj.RelocationAbsolute;
import ghidra.program.model.relocobj.RelocationRelativePC;
import ghidra.program.model.relocobj.RelocationTable;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.Symbol;

public class ExportDelinkTables extends GhidraScript {
	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		MemoryBlock text = currentProgram.getMemory().getBlock(".text");
		AddressSet textSet = new AddressSet(text.getStart(), text.getEnd());
		AutoAnalysisManager manager = AutoAnalysisManager.getAnalysisManager(currentProgram);
		Analyzer synthesizer = manager.getAnalyzer("Relocation table synthesizer");
		manager.scheduleOneTimeAnalysis(synthesizer, textSet);
		manager.waitForAnalysis(null, monitor);

		// Each line: address, kind (A absolute, R PC-relative), width, bitmask,
		// target, addend, and for a transparent PC-relative relocation "T:" and the
		// primary reference targets of its instruction, which decide whether the
		// exporter drops it for a given unit; "-" otherwise.
		int relocations = 0;
		try (PrintWriter out = new PrintWriter(args[0])) {
			Iterator<Relocation> it = RelocationTable.get(currentProgram).getRelocations(textSet);
			while (it.hasNext()) {
				Relocation r = it.next();
				String kind = r instanceof RelocationAbsolute ? "A"
						: r instanceof RelocationRelativePC ? "R" : "?";
				String refs = "-";
				if (r instanceof RelocationRelativePC && r.isTransparent()) {
					CodeUnit unit = currentProgram.getListing().getCodeUnitContaining(r.getAddress());
					StringJoiner targets = new StringJoiner(",", "T:", "");
					for (Reference ref : currentProgram.getReferenceManager()
							.getReferencesFrom(unit.getAddress())) {
						if (ref.isPrimary()) {
							targets.add(String.format("%08X", ref.getToAddress().getOffset()));
						}
					}
					refs = targets.toString();
				}
				out.printf("%08X\t%s\t%d\t%X\t%08X\t%d\t%s%n", r.getAddress().getOffset(), kind,
					r.getWidth(), r.getBitmask(), r.getTarget().getOffset(), r.getAddend(), refs);
				relocations++;
			}
		}

		// These are the exporter's defaults: the MSVC name preference, and static
		// visibility for dynamic symbols, for symbols inside a function and for
		// switch data.
		Predicate<Symbol> isStatic = new IsSymbolDynamic()
				.or(new IsSymbolInsideFunction())
				.or(new IsSymbolNameMatchingRegex(IsSymbolNameMatchingRegex.DEFAULT_PATTERN));
		Map<Address, SymbolInformation> infos = StreamSupport
				.stream(currentProgram.getSymbolTable().getAllSymbols(true).spliterator(), false)
				.filter(s -> s.getAddress().isMemoryAddress())
				.collect(new SymbolInformationCollector(SymbolPreference.MSVC));
		try (PrintWriter out = new PrintWriter(args[1])) {
			for (Map.Entry<Address, SymbolInformation> e : new TreeMap<>(infos).entrySet()) {
				Symbol symbol = e.getValue().getSymbol();
				out.printf("%08X\t%d\t%d\t%s%n", e.getKey().getOffset(),
					symbol.getObject() instanceof Function ? 1 : 0,
					isStatic.test(symbol) ? 1 : 0, e.getValue().getName());
			}
		}
		println("delink tables written: relocations " + relocations + ", symbols " + infos.size());
	}
}
