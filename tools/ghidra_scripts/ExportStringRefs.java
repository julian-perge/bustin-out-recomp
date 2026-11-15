//Writes one line per function and string it references: the function's entry,
//the string's address and the escaped text, separated by tabs. Argument: the
//output file. A string is defined string data, or else four to 1023 printable
//ASCII or UTF-16LE characters ending in a zero. Either way it lies outside
//every function.
//@category Project

import java.io.PrintWriter;
import java.util.HashSet;
import java.util.Set;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;

public class ExportStringRefs extends GhidraScript {
	@Override
	public void run() throws Exception {
		int lines = 0;
		int functions = 0;
		try (PrintWriter out = new PrintWriter(getScriptArgs()[0])) {
			for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
				if (f.isExternal()) {
					continue;
				}
				Set<Long> seen = new HashSet<>();
				for (Instruction ins : currentProgram.getListing().getInstructions(f.getBody(), true)) {
					for (Reference r : ins.getReferencesFrom()) {
						Address to = r.getToAddress();
						if (!to.isMemoryAddress() || !r.getReferenceType().isData()
							|| getFunctionContaining(to) != null || seen.contains(to.getOffset())) {
							continue;
						}
						String text = stringAt(to);
						if (text == null) {
							continue;
						}
						seen.add(to.getOffset());
						out.printf("%08X\t%08X\t%s%n", f.getEntryPoint().getOffset(), to.getOffset(), escape(text));
						lines++;
					}
				}
				if (!seen.isEmpty()) {
					functions++;
				}
			}
		}
		println("string references " + lines + " in " + functions + " functions");
	}

	private String stringAt(Address a) {
		Data data = getDataAt(a);
		if (data != null && data.hasStringValue() && data.getValue() != null) {
			String value = data.getValue().toString();
			return value.isEmpty() ? null : value;
		}
		String ascii = scan(a, 1);
		return ascii != null ? ascii : scan(a, 2);
	}

	// Reads characters of the given width until a zero and returns them when there
	// are four to 1023, all printable ASCII, tab, newline or carriage return.
	// A longer run returns null, so it is not recorded as a string.
	private String scan(Address a, int width) {
		Memory memory = currentProgram.getMemory();
		StringBuilder text = new StringBuilder();
		try {
			for (int i = 0; i < 1024; i++) {
				Address at = a.add((long) i * width);
				int c = memory.getByte(at) & 0xff;
				if (width == 2 && memory.getByte(at.add(1)) != 0) {
					return null;
				}
				if (c == 0) {
					return text.length() >= 4 ? text.toString() : null;
				}
				if ((c < 0x20 && c != '\t' && c != '\n' && c != '\r') || c > 0x7e) {
					return null;
				}
				text.append((char) c);
			}
		} catch (Exception e) {
			return null;
		}
		return null;
	}

	private static String escape(String s) {
		StringBuilder out = new StringBuilder();
		for (char c : s.toCharArray()) {
			switch (c) {
				case '\\' -> out.append("\\\\");
				case '\t' -> out.append("\\t");
				case '\n' -> out.append("\\n");
				case '\r' -> out.append("\\r");
				default -> {
					if (c >= 0x20 && c < 0x7f) {
						out.append(c);
					} else {
						out.append(String.format("\\u%04x", (int) c));
					}
				}
			}
		}
		return out.toString();
	}
}
