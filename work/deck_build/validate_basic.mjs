import path from "node:path";
import { pathToFileURL } from "node:url";

const workspaceDir = process.env.DECK_VALIDATION_WORKSPACE;
if (!workspaceDir) throw new Error("DECK_VALIDATION_WORKSPACE is required.");
const skillDir = "C:/Users/karti/.codex/plugins/cache/openai-primary-runtime/presentations/26.1119.11507/skills/presentations";
const { finalizePresentation } = await import(pathToFileURL(path.join(skillDir, "container_tools", "artifact_tool_utils.mjs")).href);
const candidatePath = path.join(workspaceDir, "candidate.pptx");
const finalPath = path.join(workspaceDir, "validated_showcase.pptx");
const reportPath = path.join(workspaceDir, "validation.json");

const result = await finalizePresentation({
  explicitTotalSlideCount: 10,
  requiredNativeChartOwnerSlides: [],
  requiredNativeTableOwnerSlides: [],
  fontPolicy: { basis: "design", families: ["Arial"] },
  workspaceDir,
  candidatePath,
  finalPath,
  pythonExecutable: process.env.RUNTIME_PYTHON,
  integrityValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_layout_geometry.py"),
  layoutArgs: ["--expected-slide-size-emu", "12192000,6858000", "--validate-bullet-geometry", "--validate-heading-fit"],
  verifyArtifactToolImport: true,
  receiptPath: reportPath,
});

console.log(JSON.stringify({ result, finalPath, reportPath }, null, 2));
