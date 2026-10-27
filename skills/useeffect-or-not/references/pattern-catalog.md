# Effect pattern catalog

## Contents

- [Derived values stored in state](#derived-values-stored-in-state)
- [Controlled values mirrored locally](#controlled-values-mirrored-locally)
- [User actions relayed through effects](#user-actions-relayed-through-effects)
- [Effect chains](#effect-chains)
- [State reset after identity changes](#state-reset-after-identity-changes)
- [Raw data fetching](#raw-data-fetching)
- [External store snapshots copied into state](#external-store-snapshots-copied-into-state)
- [Competing stores reconciled continuously](#competing-stores-reconciled-continuously)
- [Application initialization hidden in mount effects](#application-initialization-hidden-in-mount-effects)
- [Valid external synchronization](#valid-external-synchronization)
- [Effect review checks](#effect-review-checks)

## Derived values stored in state

### Signal

An effect calls a state setter with a value calculated entirely from props,
state, context, or selectors.

```tsx
const [visibleItems, setVisibleItems] = useState<Item[]>([]);

useEffect(() => {
  setVisibleItems(filterItems(items, query));
}, [items, query]);
```

### Why it fails

The component commits once with a stale value and then renders again. The
stored value can also drift from its inputs.

### Replace it

```tsx
const visibleItems = filterItems(items, query);
```

Use `useMemo` only if the calculation is expensive or a stable reference is
part of another API's contract.

### Valid exception

The value is a user-editable draft that intentionally diverges from its
initial input. In that case, name the draft and define when it is committed or
discarded.

## Controlled values mirrored locally

### Signal

Local state starts from a prop or context value. One effect copies later
external changes into local state, and another effect reports local changes
back to the owner.

```tsx
const [selection, setSelection] = useState(value);

useEffect(() => setSelection(value), [value]);
useEffect(() => onChange(selection), [selection, onChange]);
```

### Why it fails

The component has two owners. Updates travel through a render and an effect,
which can produce stale frames, feedback loops, and ordering bugs.

### Replace it

Render from the controlled value and report the next value from the handler.

```tsx
<Select value={value} onChange={(nextValue) => onChange(nextValue)} />
```

If the control needs an uncommitted draft, keep only the draft locally and
define an explicit commit boundary such as blur, Enter, Apply, or Save.

### Valid exception

An imperative editor owns transient internal state that cannot be controlled
per keystroke. Synchronize at a documented boundary and guard against
overwriting a dirty draft.

## User actions relayed through effects

### Signal

An event handler sets state only so an effect can submit, navigate, notify,
track analytics, or call `onChange`.

```tsx
function handleSubmit() {
  setShouldSubmit(true);
}

useEffect(() => {
  if (shouldSubmit) submitForm();
}, [shouldSubmit]);
```

### Why it fails

The work runs after a render instead of directly from the user action, so it
may replay after remounting or hydration.

### Replace it

Call the work from the handler or the mutation callback that knows the action
succeeded.

```tsx
function handleSubmit() {
  submitForm();
}
```

### Valid exception

The work is caused by visibility or mount rather than a particular action. An
impression event can be lifecycle-driven if its deduplication contract is
clear.

## Effect chains

### Signal

One effect sets state that triggers a second effect, or state is used as an
event queue between effects.

### Why it fails

Each link adds a render, exposes intermediate states, and makes ordering depend
on component lifecycle rather than the original transition.

### Replace it

Calculate the complete next state in the event, reducer, or owner action. Keep
values that can be calculated out of state.

### Valid exception

Separate effects may synchronize independent external systems. They should not
communicate by writing React state solely to wake each other up.

## State reset after identity changes

### Signal

An effect clears inputs, selection, errors, or draft state whenever an ID,
route, tab, modal, or selected entity changes.

### Why it fails

Children render once with state from the previous identity. Nested state is
easy to miss, and the reset logic spreads across the subtree.

### Replace it

Give the stateful subtree a key that represents its identity.

```tsx
<Editor key={documentId} documentId={documentId} />
```

If only one field should reset, perform that reset in the explicit navigation
or selection handler that changes the identity.

### Valid exception

The component intentionally preserves most state across identities and only a
specific draft field must change. Keep the transition explicit and test both
preserved and reset fields.

## Raw data fetching

### Signal

An effect owns request start, loading state, error state, cancellation, and
response storage.

### Why it fails

Every component recreates caching, deduplication, retries, cancellation, and
stale-response handling. Remounts can duplicate requests or allow an older
response to win.

### Replace it

Use the repository's query hook, route loader, or data service. Keep mutations
in event handlers or mutation hooks.

### Valid exception

If no shared data primitive exists, an effect may own the request. Abort stale
requests, clean up, and expose every request state.

## External store snapshots copied into state

### Signal

An effect subscribes to a browser API, app store, observable, or custom
event emitter and copies each snapshot into local state.

### Why it fails

Manual subscriptions can miss updates between render and subscription, tear
under concurrent rendering, or keep broad subscriptions alive.

### Replace it

Use the store's React selector hook. For a custom external store, use
`useSyncExternalStore` with stable `subscribe` and `getSnapshot` functions.

### Valid exception

An imperative library emits events that are not readable as a snapshot. An
effect may own that event subscription, but it still needs symmetrical cleanup
and a narrow state update.

## Competing stores reconciled continuously

### Signal

An effect copies a query result into an app store, an app store into a query cache, persisted
state into a live store, or context into another store whenever either changes.

### Why it fails

Both sources appear authoritative. A stale snapshot can overwrite the live
value, and bidirectional synchronization can loop.

### Replace it

Choose one runtime owner. Hydrate once at an explicit empty or bootstrap
boundary, then route all later changes through the owner.

### Valid exception

If two systems must coexist, define which direction data flows, which source
wins, and when the bridge is removed.

## Application initialization hidden in mount effects

### Signal

A top-level component uses an empty-dependency effect for work that must happen
once per application load, regardless of component remounts.

### Why it fails

Component mount is not application lifetime. Strict Mode and future tree
changes can repeat the initialization.

### Replace it

Use the application bootstrap, module initialization where safe, or an
idempotent service with explicit lifetime ownership.

### Valid exception

The resource genuinely belongs to that component instance. In that case,
repeatable setup and cleanup are correct.

## Valid external synchronization

An effect is appropriate when it owns a lifecycle outside React, including:

- creating, updating, and destroying an imperative widget;
- animating or measuring committed DOM;
- starting and stopping a timer, observer, media query, or browser listener;
- opening and closing a WebSocket, EventSource, or hardware connection;
- synchronizing a global browser API such as `document.title`;
- registering with an external service that requires teardown.

Setup and cleanup must be symmetrical, every reactive input must be
represented, and repeated setup must be safe.

## Effect review checks

Before approving an effect, answer all of these:

- What external system is being synchronized?
- Why can the work not happen during render or in the causing event?
- Does the effect write React state, and is that state truly independent?
- Can setup run twice without corrupting state or duplicating work?
- Does cleanup undo the exact setup for the same resource instance?
- Can an old async result overwrite a newer one?
- Do dependencies describe the synchronization rather than suppress it?
- Would a selector hook, query hook, `key`, reducer, or controlled prop remove
  the synchronization entirely?
