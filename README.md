# Sloths Blender Tools
<img width="1280" height="640" alt="Untitled (1)" src="https://github.com/user-attachments/assets/65adfdf9-0fc3-458c-b464-2501ed19a77c" />
---
A small set of Blender editor tools bundled into a simple sidebar panel with one-click buttons.  
Find it in: **3D Viewport → N Panel → Sloth’s Tools**

##Website: https://watersloth.carrd.co/

---

## Included Tools

### 1) Clear Custom Split Normals (Selected)
Clears **custom split normals** on all currently selected **Mesh** objects.

**What it does**
- Iterates over selected meshes
- Switches to Edit Mode per object
- Selects all faces
- Runs Blender’s *Clear Custom Split Normals* operation

**When to use**
- After importing meshes that come with baked/custom normals you don’t want
- When shading looks “stuck” or inconsistent due to custom normal data

---

### 2) Remove Alpha From All Materials
Forces materials to render as **fully opaque**, and optionally removes alpha inputs.

**What it does**
- Loops through all materials in the file
- Sets:
  - `blend_method = OPAQUE` (when available)
  - `shadow_method = OPAQUE` (when available)
- Finds the first **Principled BSDF** in each material:
  - Sets **Alpha = 1.0**
  - Optionally disconnects any node links feeding Alpha (toggle in UI)

**When to use**
- Imported materials are incorrectly transparent
- You want to remove alpha-based cutouts/transparency globally

---

### 3) Set Roughness For All Materials
Sets a consistent **roughness value** on all Principled materials, optionally removing roughness textures.

**What it does**
- Loops through all materials using nodes
- Finds the first **Principled BSDF** in each material
- Sets **Roughness** to the UI value (0–1)
- Optionally disconnects any node links feeding Roughness (toggle in UI)

**When to use**
- You need a quick “matte pass” for previewing assets
- You want to override roughness maps globally for troubleshooting or lookdev

---

### 4) Remap Image Paths to `.png`
Updates image texture node filepaths to point at `.png` versions of common formats.

**What it does**
- Loops through all materials
- Finds **Image Texture** nodes (`TEX_IMAGE`)
- If the image filepath ends with a selected extension:
  - `.dds`
  - `.jpg` / `.jpeg`
  - `.webp`
- Replaces the extension with `.png` (path only — does not convert files)
- Updates the node name and image datablock name for UI clarity

**When to use**
- You’ve batch-converted textures to PNG externally and want Blender to relink fast
- You’re standardizing texture formats across a project

---

### 5) Clean Trees (Selected)
A mesh cleanup helper designed for “tree-like” imports, removing faces that don’t match the main body.

**What it does**
- Runs on selected Mesh objects one at a time
- In Edit Mode:
  - Finds the **largest face** by area
  - Uses **Select Similar → Area** with a configurable threshold
  - Inverts selection and deletes the remaining faces

**UI Setting**
- **Area Threshold**: smaller = stricter match

**When to use**
- Imported trees have extra geometry chunks you want removed quickly
- You want a fast “keep the main mass” cleanup pass

---

## Installation

### Install (zip)
1. Download the latest release `.zip` from GitHub.
2. In Blender: **Edit → Preferences → Add-ons → Install…**
3. Select the downloaded zip and enable the add-on.

### Where to find the tools
**3D Viewport → N Panel → Sloth’s Tools**

---

## Notes / Safety
- Most tools modify many objects/materials at once — save or duplicate your file first if needed.
- Some tools intentionally override material behavior globally (Alpha/Roughness).

---

## License
MIT (or your chosen license — update this section to match your repo).
