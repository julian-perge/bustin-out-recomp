//Creates a function at each listed address that is not already inside one, then
//runs auto-analysis on the changes. Arguments: a file with a hex address at the
//start of each line, a file to write each rejected address and its reason to,
//and optionally the word "starts", which also rejects as missing every listed
//address that does not end up as a function start.
//@category Project

import java.io.File;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.BookmarkManager;
import ghidra.program.model.listing.BookmarkType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;

public class CreateFunctions extends GhidraScript {
	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		List<Long> offsets = new ArrayList<>();
		for (String line : Files.readAllLines(new File(args[0]).toPath())) {
			String field = line.trim().split("\\s+")[0];
			if (!field.isEmpty()) {
				offsets.add(Long.parseLong(field, 16));
			}
		}
		Listing listing = currentProgram.getListing();
		List<String> rejected = new ArrayList<>();
		int present = 0;

		// A 0xCC byte inside an instruction looks like padding, so a listed address
		// can fall in the middle of real code. Disassembling from the lowest address
		// up lays down the real instructions first, and an address that lands inside
		// one of them, or inside an existing function's instruction, is rejected.
		offsets.sort(Long::compare);
		AddressSet listedCode = new AddressSet();
		List<Address> accepted = new ArrayList<>();
		for (long offset : offsets) {
			Address start = toAddr(offset);
			if (getFunctionContaining(start) != null) {
				present++;
				continue;
			}
			if (listing.getDefinedDataContaining(start) != null) {
				rejected.add(String.format("%08X data", offset));
				continue;
			}
			Instruction covering = listing.getInstructionContaining(start);
			if (covering != null && covering.getMinAddress().compareTo(start) < 0
				&& (listedCode.contains(covering.getMinAddress())
					|| getFunctionContaining(covering.getMinAddress()) != null)) {
				rejected.add(String.format("%08X mid-instruction", offset));
				continue;
			}
			Attempt attempt = attemptAt(start);
			// Ghidra's analysis disassembles from any constant that looks like a code
			// address, so a gap can hold instructions that start inside real ones
			// and conflict with disassembly from the candidate. Those instructions
			// are removed and the candidate is disassembled once more.
			if (!attempt.errors().isEmpty()) {
				undo(attempt);
				clearStrayCode(start);
				attempt = attemptAt(start);
			}
			// The disassembler marks bytes that do not decode with an error
			// bookmark. Flow that reaches such bytes means the address is not
			// the start of real code, so its instructions and marks are removed.
			if (!attempt.errors().isEmpty()) {
				undo(attempt);
				rejected.add(String.format("%08X bad-instruction %s", offset, attempt.errors().getMinAddress()));
				continue;
			}
			listedCode.add(attempt.code());
			accepted.add(start);
		}

		// Ghidra ends a new function's body where the next function starts, so
		// creating the highest address first keeps each body from running on
		// into code that a lower address in the list should own.
		int created = 0;
		for (Address start : accepted.reversed()) {
			if (listing.getInstructionAt(start) == null || createFunction(start, null) == null) {
				rejected.add(String.format("%08X no-function", start.getOffset()));
				continue;
			}
			created++;
		}
		analyzeChanges(currentProgram);

		// A 0xCC byte can also be the last byte of a real instruction, such as the
		// register operand of an SSE multiply, so a listed address can sit where
		// code simply continues. A function this run created where the instruction
		// before it falls through to it is removed again, and the function it cut
		// short gets its body recomputed.
		for (Address start : accepted) {
			Function function = getFunctionAt(start);
			Instruction before = listing.getInstructionContaining(start.previous());
			if (function == null || before == null || before.getMnemonicString().equals("INT3")
				|| !start.equals(before.getFallThrough())) {
				continue;
			}
			removeFunction(function);
			created--;
			rejected.add(String.format("%08X falls-through", start.getOffset()));
			Function owner = getFunctionContaining(before.getMinAddress());
			if (owner != null) {
				CreateFunctionCmd.fixupFunctionBody(currentProgram, owner, monitor);
			}
		}
		// Analysis can still make a function at a rejected address, for example
		// from a vtable that points to it, so an address counts as rejected only
		// if it is still not the start of a function afterwards.
		rejected.removeIf(line -> getFunctionAt(toAddr(Long.parseLong(line.split(" ")[0], 16))) != null);
		if (args.length > 2 && args[2].equals("starts")) {
			Set<String> listed = new HashSet<>();
			for (String line : rejected) {
				listed.add(line.split(" ")[0]);
			}
			for (long offset : offsets) {
				String hex = String.format("%08X", offset);
				if (getFunctionAt(toAddr(offset)) == null && !listed.contains(hex)) {
					rejected.add(hex + " missing");
				}
			}
		}
		Files.write(new File(args[1]).toPath(), rejected);
		println("functions created " + created + ", already present " + present
			+ ", rejected " + rejected.size() + ", total "
			+ currentProgram.getFunctionManager().getFunctionCount());
	}

	private record Attempt(AddressSet code, AddressSet newMarks, AddressSet errors) {
	}

	// Disassembles from start and returns the new instructions, the error
	// bookmarks this added, and the errors: those new marks, plus each older mark
	// at an address the flow reached that still holds no instruction. The older
	// marks count because the disassembler does not mark an address twice, and
	// only empty ones count because a mark on an instruction is about something
	// else, such as a call into memory that does not exist.
	private Attempt attemptAt(Address start) {
		BookmarkManager bookmarks = currentProgram.getBookmarkManager();
		AddressSet before = new AddressSet(bookmarks.getBookmarkAddresses(BookmarkType.ERROR));
		DisassembleCommand command = new DisassembleCommand(start, null, true);
		command.applyTo(currentProgram, monitor);
		AddressSet code = command.getDisassembledAddressSet();
		AddressSet after = new AddressSet(bookmarks.getBookmarkAddresses(BookmarkType.ERROR));
		AddressSet reached = new AddressSet(start);
		for (Instruction i : currentProgram.getListing().getInstructions(code, true)) {
			reached.add(i.getMinAddress());
			for (Address to : i.getFlows()) {
				reached.add(to);
			}
			if (i.getFallThrough() != null) {
				reached.add(i.getFallThrough());
			}
		}
		AddressSet newMarks = after.subtract(before);
		AddressSet errors = new AddressSet(newMarks);
		for (Address a : before.intersect(reached).getAddresses(true)) {
			if (currentProgram.getListing().getInstructionAt(a) == null) {
				errors.add(a);
			}
		}
		return new Attempt(code, newMarks, errors);
	}

	private void undo(Attempt attempt) throws Exception {
		clearListing(attempt.code());
		currentProgram.getBookmarkManager().removeBookmarks(attempt.newMarks(), BookmarkType.ERROR, monitor);
	}

	// Removes the instructions that belong to no function from the one covering
	// start up to the next function or the end of the memory block.
	private void clearStrayCode(Address start) {
		Listing listing = currentProgram.getListing();
		Address end = getMemoryBlock(start).getEnd();
		Function next = getFunctionAfter(start);
		if (next != null && next.getEntryPoint().compareTo(end) <= 0) {
			end = next.getEntryPoint().previous();
		}
		Instruction first = listing.getInstructionContaining(start);
		Address from = first != null ? first.getMinAddress() : start;
		List<Instruction> stray = new ArrayList<>();
		for (Instruction i : listing.getInstructions(new AddressSet(from, end), true)) {
			if (getFunctionContaining(i.getMinAddress()) == null) {
				stray.add(i);
			}
		}
		for (Instruction i : stray) {
			listing.clearCodeUnits(i.getMinAddress(), i.getMaxAddress(), false);
		}
	}
}
