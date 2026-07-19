# Current failure analysis

This note covers the historical `iwm` prototype summarized in the main README,
not the later Virgil result.

## Observed result

The prototype completed zero official ARC-AGI-3 levels. Its offline toy demos
worked, but the live environment exposed three interacting failures.

## Failure modes

1. **Pixel-first deltas polluted the evidence.** HUD changes, animation, and
   unrelated pixel differences were treated like game mechanics. The rule
   learner accumulated noisy effects instead of compact object-level changes.
2. **Parameterized clicks were not grounded.** `ACTION6(0,0)` could enter the
   evidence as though it represented the click action generally, even though a
   click's coordinates are the action. Rules learned from that representation
   could not transfer to other targets.
3. **One-example rules became overconfident.** A transition observed once could
   become an executable rule without enough counterexamples or uncertainty
   tracking. Planning inside a wrong rule model then amplified the initial
   mistake.

## What changed in later work

The later prototypes moved evaluation toward typed scenes, explicit action
data, replay verification, identity baselines, and divergence checks. The
important lesson was not that a world-model loop is sufficient by itself, but
that every abstraction entering the loop must remain grounded in observations
and falsifiable by replay.
