import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const skillDir = "C:/Users/karti/.codex/plugins/cache/openai-primary-runtime/presentations/26.1119.11507/skills/presentations";
const { finalizePresentation } = await import(pathToFileURL(path.join(skillDir, "container_tools", "artifact_tool_utils.mjs")).href);
const candidatePath = path.join(root, "work", "deck_tmp", "Delhi_Groundwater_Showcase_draft.pptx");
const finalPath = path.join(root, "presentations", "Delhi_Groundwater_Monitoring_Showcase_10min.pptx");
const reportPath = path.join(root, "work", "deck_tmp", "Delhi_Groundwater_Showcase_validation.json");
const requirements = {
  explicitTotalSlideCount: 10,
  requiredNativeChartOwnerSlides: [7],
  requiredNativeTableOwnerSlides: [],
  fontPolicy: { basis: "design", families: ["Arial"] },
};

const result = await finalizePresentation({
  ...requirements,
  workspaceDir: root,
  candidatePath,
  finalPath,
  pythonExecutable: process.env.RUNTIME_PYTHON,
  integrityValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_layout_geometry.py"),
  layoutArgs: [
    "--expected-slide-size-emu", "12192000,6858000",
    "--validate-bullet-geometry",
    "--validate-heading-fit",
  ],
  verifyArtifactToolImport: true,
  receiptPath: reportPath,
});

console.log(JSON.stringify({ result, finalPath, reportPath }, null, 2));
