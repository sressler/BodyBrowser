# BodyBrowser: CAESAR™ Scan Browser

A web browser for 3D body scans from the CAESAR™ anthropometric survey (US, Italy and the Netherlands). It shows the scans with their anatomical landmarks, filters subjects by measurement and sex, lays out up to 200 bodies at once, and compares two bodies side by side or superimposed. It runs entirely in the browser, uses three.js, and reads scans from your own disk. Nothing is uploaded.

By Sandy Ressler.

### [▶ RUN ME: open the live CAESAR™ Scan Browser](https://claude.ai/artifact/HT5aBXNzxDDL95aFZerRgt)

![Multi mode, Cube layout with fog and the cube outline](docs/images/multi_cube.png)

## Contents of this repository

| Path | What it is |
| --- | --- |
| `index.html` | The browser: one self-contained page. The measurement and sex tables for all 4,459 subjects are built in. |
| `help.html` | The help page linked from the browser. |
| `samples/*.txt` | The built-in sample set: 60 scans (30 subjects, each with a standing *a* and a seated *b* scan). Each is a meshopt-compressed GLB stored as base64 text. |
| `tools/ply2glb.py` | Converts one CAESAR PLY scan (`.ply` or `.ply.gz`), plus its `.lnd` landmark file, to a single GLB with vertex colors, normals and landmarks as named nodes. |
| `tools/convert_folders.py` | Batch, resumable, time-boxed conversion of whole CAESAR data folders (`a1`–`a21`, `b1`–`b21`, …) into each folder's `gltf/` subfolder. |
| `docs/images/` | Screenshots used in this README. |

The full CAESAR scan data (PLY, landmark and measurement files) is not included in this repository.

## Running it

Serve the folder with any static web server and open `index.html`, for example:

```sh
python3 -m http.server 8000
# then open http://localhost:8000/
```

The page needs an internet connection the first time it loads, to fetch three.js 0.160 from jsDelivr. When it opens, it loads the sample set into Multi mode with the Cube layout and fog on. Use **Add folder…** to add your own CAESAR folders (for example `CAESARall/data/a2`), or the `gltf` folders made by the converter.

## Converting scans to GLB

Requires Python 3 and numpy.

```sh
# one file
python3 -c "import sys; sys.path.insert(0,'tools'); from ply2glb import convert; \
  print(convert('a2/scans/csr0250a.ply.gz','a2/landmarks/csr0250a.lnd','csr0250a.glb'))"

# whole folders: status only, then repeated time-boxed steps (re-run until REMAINING is 0)
python3 tools/convert_folders.py /path/to/CAESARall/data 'a\d+' 0
python3 tools/convert_folders.py /path/to/CAESARall/data 'a\d+' 110
```

The output is in metres and rotated from the scanner's Z-up to glTF's Y-up, (x, y, z) → (x, z, −y). Landmarks are stored as nodes named like `11 Suprasternale` under a `landmarks` node, with `extras.landmark_id`. The sample files were further compressed with `gltfpack -cc -kn -ke`.

## Screenshots

**Multi mode, Wall layout**

![Multi mode, Wall layout](docs/images/multi_wall.png)

**Compare mode:** standing and seated scans of one subject superimposed, B tinted orange at 60% opacity

![Compare mode](docs/images/compare.png)

**Single mode** with landmarks colored by body region

![Single mode](docs/images/single.png)

## Help

The text below is the same as `help.html`.

The browser displays 3D body scans from the CAESAR anthropometric survey (US, Italy and Netherlands), with their anatomical landmarks and measurements. It reads scans straight from your disk: nothing is uploaded.

- 1\. Getting started
- 2\. The file list
- 3\. Single mode
- 4\. Multi mode
- 5\. Compare mode
- 6\. Moving around and display options
- 7\. Landmarks
- 7a\. Tape measures and definitions
- 8\. Measurement and sex filters
- 9\. Keyboard and mouse summary
- 10\. About the data
- 11\. Limits and troubleshooting

### 1. Getting started

**When the page opens** it loads the built-in sample set (60 scans) into **Multi** mode with the **Cube** layout and fog turned on. The bodies appear one after another as they download. Use Clear scene and Clear to start fresh with your own folders.

1. Click Add folder… and choose a folder from `CAESARall/data`, for example `a2`.
2. The browser finds every scan inside it: `scans/*.ply.gz` (original scanner files), `gltf/*.glb` (converted files), and the matching `landmarks/*.lnd` files.
3. The first scan is displayed automatically. Click any other entry in the list to display it.

Folders add up: choose `a2`, then `b2`, then `a2/gltf`, and all of them appear in one list. Add files… adds individual files, and you can also drag files onto the 3D view. Clear empties the list and removes every body from the scene.

**No scans on this computer?** Click Load sample set (or the link in the empty view). It loads 60 scans stored with this page: 30 people (15 men and 15 women spread from the shortest to the tallest in the sample), each with a standing (*a*) and a matching seated (*b*) scan, which suit Compare mode. These are compressed GLBs (about 1.3 MB each instead of 8 MB) with colors and landmarks kept; positions are stored to about 0.1 mm. The sample set adds to the list like a folder does.

**Which folder to pick?** `a` folders hold standing scans, `b` seated, `c` a second seated pose. Picking a folder's parent (e.g. `a2`) gives you both its PLY and GLB files; picking `a2/gltf` gives just the GLBs. A browser can only read inside the folder you pick, so files in parent folders are not seen. The measurement data is built in, so you don't need them.

### 2. The file list

- Each entry shows the scan name, a PLY or GLB tag, the subject's sex (M/F) and measurement values, and the file size.
- A  green dot on a PLY entry means a matching landmark file was found. GLB files carry their landmarks inside.
- **Show: All / PLY / GLB** limits the list to one file type.
- The **Filter** box matches part of the name, e.g. `030` or `nl_`.
- The measurement and sex filters (section 8) also narrow the list.
- Download 1st selected (below the Show buttons) saves the first selected scan in the list: the one shown in Single mode, the first body in the scene in Multi mode, or the first of A/B in Compare mode. In the Claude artifact viewer the file arrives inside a .zip; on the hosted website it downloads as is.
- **Shift-click** (Multi mode): click one scan, then shift-click another to add every scan between them, as in the Finder. To remove a range, click a scan that is in the scene (which removes it), then shift-click another: every scan between them is removed.

### 3. Single mode

One body at a time. Click a list entry, or use ◀ Prev Next ▶ or `↑` `↓` to step through the list. The header shows vertex and triangle counts, the scan height, the subject's sex and the values of the three selected measurements.

### 4. Multi mode

Many bodies at once (up to 200). Clicking a list entry **adds** that body to the scene; clicking it again **removes** it. Bodies in the scene are highlighted in the list. Every body is turned to face the front, using its landmarks, and has a name tag underneath.

| Layout | Arrangement |
| --- | --- |
| Wall | A grid of rows stacked upward and columns side by side, starting top-left. The number of columns follows the window's shape. |
| Cube | A 3D lattice with equal spacing in all three directions (27 bodies → 3×3×3). The camera starts at a three-quarter view from above. Fly inside with WASD. **Cube outline: On / Off** shows or hides a gray wireframe of the cube the bodies sit in. Fog helps show depth here. |
| Line | One horizontal row. Each body gets exactly its own width plus a 15 cm gap, so neighbors never touch. |

- Add all shown adds every scan currently in the list (after filters). Use the filters first to choose a group.
- Clear scene removes all bodies but keeps the list.
- Bodies that stop passing a filter are hidden, and the layout closes up the gaps.

### 5. Compare mode

Two bodies, A and B, for side-by-side or overlaid comparison.

- **Choosing bodies:** the highlighted slot receives the next scan you click in the list. After A is filled, B is highlighted automatically. Press Pick on a slot to replace just that one. Clicking a scan that is already in a slot removes it.
- **Opacity** (per body) makes it translucent so the other shows through. The defaults are A 100%, B 60%.
- **Tint** (per body) colors it blue (A) or orange (B) so overlapping surfaces are easy to tell apart.
- **Separation** slider: the distance between the two bodies' centers. At 0 cm they overlap completely; dragging moves A left and B right.
- Superimposed jumps to 0 cm. Side by side jumps to the distance where their nearest edges are 15 cm apart.
- The header shows both scan heights, the value of the first checked measurement (stature if none), and the difference B − A.

### 6. Moving around and display options

#### Mouse

- Drag to rotate · scroll to zoom · right-drag (or two-finger drag) to pan.

#### Keyboard flying

`W`/`S` forward and back · `A`/`D` left and right · `E`/`Q` up and down · hold `Shift` for 3× speed. The rotation point moves with you, so after flying somewhere the mouse rotates around your new position. Speed scales with the size of the scene.

#### Panel buttons

|  |  |
| --- | --- |
| Scan color Shaded Wire | Show the scanner's own color, plain gray shading, or the triangle mesh. |
| Front Side Back Top | Standard views, lined up with the direction the body faces. |
| Auto-rotate | Slowly spin the view. |
| Fit all | Reframe the camera on everything in the scene. |
| Fog + slider | Fade farther bodies into the background (distance fog). The slider sets the strength; the fog follows the camera, so whatever is nearest stays clear. |
| Names | Show or hide the file-name tags under the bodies (Multi and Compare). |
| – / + | Collapse or expand the control panel. |

### 7. Landmarks

Landmarks are the anatomical points marked on each scan (about 73 for standing scans), drawn as small spheres colored by body region:

Head & neck   Torso   Arms & hands   Legs & feet   Crotch (a computed point between the legs, not on the surface)

- **Hover** over a sphere to see its number and name.
- **Click** a sphere to pin a label that stays on screen and follows it as you move. Click it again to remove the label. Pinned landmarks are drawn larger.
- Pins go by landmark number, so pinning "11. Suprasternale" labels it on *every* body in the scene, and the pins stay when you switch scans.
- A pinned label is dimmed when its point is on the far side of a body (only with 12 or fewer bodies, to keep things fast).
- Show hides or shows all spheres. X-ray draws them through the body. Clear labels removes all pins. The **size** slider changes the sphere size.

### 7a. Tape measures and definitions

Pick up to two measurements from the **Tape measures** menus in the left panel, above the measurement filters. Tape 1 is drawn in yellow and tape 2 in blue, both with inch marks, on every body in the scene, as described in the *CAESAR Final Report, Vol. II: Demographic and Measurement Descriptions* (Air Force Research Laboratory, 2002):

- **Circumferences** wrap around the scan the way a tape does, bridging hollows (chest at the bust points, waist at the preferred-waist landmark, hip at the table's maximum-hip height, neck base, armscye, thigh, ankle, head, hand, vertical trunk).
- **Surface lengths** run over the body between landmarks (arm lengths, total crotch length, waist front length).
- **Breadths and short lengths** are shown as a caliper (shoulder, head, bizygomatic, foot, hand, face).
- **Heights** stand beside the body from the floor, or from the seat on seated scans, with the table value as the tape length.

The readout and labels give the table value (measured by hand) and, where the scan allows, the length of the tape on the scan. They differ because the scan posture is not the measuring posture (for example, arm lengths were taken with the arm bent and the fist on the hip). Seated measures appear only on seated (b/c) scans and standing measures only on standing (a) scans. Weight, skinfolds and thumb-tip reach are not drawn.

In Multi mode the tapes are drawn on every body, a few per frame, so they appear one after another in a large scene. Labels on the bodies are shown only when there are 12 or fewer.

A card at the bottom right shows the report's description, method, instrument, ISO 7250 reference and line drawing for the chosen measurement, with its page number. With two tapes on, tabs switch between them. Use – on the card to fold it.

### 8. Measurement and sex filters

#### Sex

**All / Male / Female** radio buttons.

#### Three measurement filters

Each slot has a checkbox (on/off), a dropdown of the 45 traditional measurements, and **Min**/**Max** sliders showing inches and cm (pounds and kg for weight). Choosing a measurement resets its sliders to that measure's full range. The defaults are Stature, Weight and Chest Circumference.

- A body must pass **every** checked filter and the sex filter to be listed or shown.
- Scans missing a value for a checked measurement are hidden; the count line says how many.
- List entries show the values of the checked measurements (stature when none is checked).

**The 45 measurements**

Heights: stature, crotch, knee, waist (preferred), hip-max; sitting height, eye, acromial and elbow height sitting. Lengths: arm (spine–wrist, shoulder–wrist, shoulder–elbow), spine–shoulder, spine–elbow, buttock–knee, waist front, total crotch, foot, hand; thumb-tip reach and three trials. Breadths: shoulder, hip sitting, head, bizygomatic. Circumferences: chest, under-bust, chest girth at scye, armscye, waist, hip max, thigh, thigh max sitting, neck base, ankle, hand, head, vertical trunk. Also head length, face length, subscapular and triceps skinfolds, and weight.

The measurement and sex data for all 4,459 subjects (all a, b and c folders) is built into the page, so filters work whichever folder you pick. If you add a folder containing a `MeasurementsEnglish` file, its values replace the built-in ones. Seated (b) and second-seated (c) scans use the same subject's measurements. Under-bust circumference is blank for most men.

### 9. Keyboard and mouse summary

| Input | Action |
| --- | --- |
| Drag · scroll · right-drag | Rotate · zoom · pan |
| `W` `A` `S` `D` · `Q` `E` · `Shift` | Fly · down/up · faster |
| `↑` `↓` | Previous / next scan (Single mode) |
| Click list entry | Show (Single) · add/remove (Multi) · put in A or B (Compare) |
| `Shift`-click list entry | Add or remove the whole range, following the first-clicked scan (Multi) |
| Hover / click landmark | Show name / pin or unpin its label on every body |

Keys are ignored while you are typing in the filter box.

### 10. About the data

- **Scan names:** `csr0250a` is US/Italy subject 250, pose *a* (standing); *b* and *c* are seated poses. `nl_1001a` is Dutch subject 1001.
- **PLY scans** (`.ply.gz`): the original scanner meshes, about 150–190 thousand vertices with per-vertex color, in meters with Z pointing up. The browser stands them upright with the feet on the floor.
- **Landmark files** (`.lnd`): columns 5–7 are x, y, z in millimeters in the scan's own coordinates. Landmarks marked missing (`-999`) are skipped.
- **GLB files** (`gltf/*.glb`): converted from the PLY scans. Meters, rotated to the glTF convention (Y up), vertex colors and normals, with the landmarks stored inside as named points in a `landmarks` group. They open in Blender and other glTF viewers.
- **Facing direction:** worked out from the landmarks (back of neck → sternum) and used for the Front/Side/Back views and for turning bodies in Multi and Compare.

### 11. Limits and troubleshooting

- **Memory:** each body uses about 10 MB once loaded. 200 bodies is about 60 million triangles and 1.5–2 GB, so rotating may get slow on smaller machines.
- **"No matching landmark file":** add the folder that contains `landmarks/` (e.g. pick `a2` rather than `a2/scans`), or use the GLB version.
- **A scan disappears from the list:** check the Show buttons, the filter box, and the sex and measurement filters.
- **Odd gaps in Line layout:** stray scanner specks near the feet or stool count toward a body's width.
- **Nothing appears:** the page needs an internet connection the first time, to load the three.js 3D library.
- **Compressed GLBs** (meshopt + quantization, made with gltfpack) open in this browser and in three.js; some other glTF tools can't read meshopt-compressed files, so use the uncompressed GLBs from the `gltf` folders there.
