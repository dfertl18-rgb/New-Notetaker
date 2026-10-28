import * as THREE from "three";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";
import * as HUMAN from "./hfpkg/src/human/index.ts";
window.THREE = Object.assign({}, THREE, { RoundedBoxGeometry });
window.HF = HUMAN;
