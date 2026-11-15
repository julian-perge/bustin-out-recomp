# ADR-0017: The default flags gain /GX

- **Status:** Accepted (user decision, 2026-11-15)
- **Date:** 2026-11-15

## Context

ADR-0004 set the default flags to `/O2 /G7 /arch:SSE`. M0 chose them with 20 leaf functions, and none of those has an exception-handling frame.

The probe of issue #4 compiled a skeleton of class 1 of the thunk trial (F-0088). The original constructor 0x00047D20 starts with an exception-handling frame. At `/O2 /G7 /arch:SSE` VC71 emits no frame, so the constructor cannot match. With `/GX` added it emits the frame, and the handler, the function info, the unwind table and the funclet compare equal with the original. The constructors of all three trial classes start with such a frame.

With `/GX` added, `bodecomp.match` gives every claimed source the row it had: 3306 matched and 3 parked.

## Decision

The project default is `/O2 /G7 /arch:SSE /GX`. This amends the flag set of ADR-0004. The rest of ADR-0004 stands.

## Consequences

- A function with an exception-handling frame can match at the default flags.
- `/GX` is the VC71 spelling of `/EHsc`. It is not checked whether the game used `/EHa`, which would give other code in some functions. A function whose frame differs only by the exception model is evidence for a new decision.
- A library may still have been built with other flags (ADR-0004, F-0021).
- The test `test_default_flags_emit_an_exception_handling_frame` fails when the flag is removed.
