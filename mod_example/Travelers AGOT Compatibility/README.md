# Travelers AGOT Compatibility

This is a [Travelers](https://steamcommunity.com/sharedfiles/filedetails/?id=3082182371) compatibility patch for [A Game of Thrones](https://steamcommunity.com/sharedfiles/filedetails/?id=2962333032). For an overview of features and other changes, see the [Travelers README](https://github.com/pharaox/travelers/blob/main/README.md).

The latest version is compatible with CK3 1.14.x, Travelers 0.9.x, and AGOT 0.3.5+.

Load order:

* A Game of Thrones
* Travelers
* Travelers AGOT Compatibility (this mod)

## Overview

Travelers is already largely compatible with most mods due to its design. This compatibility patch is making it fully compatible with AGOT. It introduces the following changes:

* Reconciles changes to  `travl_on_actions.txt` and `travel_options.txt` vanilla files by both mods. The main effect is that imprisoned rulers traveling to their jailor's capital can't have entourages or add travel options, and don't get any vanilla or AGOT travel events, as intended.
* Ensures that the new travel danger events for non-ruler characters use the new AGOT terrain types.
* Ensures Travelers doesn't start travel to or from unreachable locations, such as "Ruins".
* Ensures that dragons teleport instead of traveling as they have special logic to ensure they stay in their pit or follow their rider.

## Links

* [GitHub Repository](https://github.com/pharaox/travelers_agot)
