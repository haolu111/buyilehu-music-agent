export type TabletStageConfig = {
  logicalWidth: 1024;
  logicalHeight: 768;
  orientation: "landscape";
  scaleMode: "contain";
  phonePolicy: "unsupported";
};

export const FIXED_TABLET_STAGE: TabletStageConfig = Object.freeze({
  logicalWidth: 1024,
  logicalHeight: 768,
  orientation: "landscape",
  scaleMode: "contain",
  phonePolicy: "unsupported",
});

export type TabletStageLayout = {
  scale: number;
  renderedWidth: number;
  renderedHeight: number;
  offsetX: number;
  offsetY: number;
};

export type StageDeviceState = "supported" | "tablet_portrait" | "phone_unsupported";

export function calculateTabletStageLayout(containerWidth: number, containerHeight: number): TabletStageLayout {
  const width = Math.max(0, containerWidth);
  const height = Math.max(0, containerHeight);
  const scale = Math.min(width / FIXED_TABLET_STAGE.logicalWidth, height / FIXED_TABLET_STAGE.logicalHeight) || 0;
  const renderedWidth = FIXED_TABLET_STAGE.logicalWidth * scale;
  const renderedHeight = FIXED_TABLET_STAGE.logicalHeight * scale;
  return {
    scale,
    renderedWidth,
    renderedHeight,
    offsetX: (width - renderedWidth) / 2,
    offsetY: (height - renderedHeight) / 2,
  };
}

export function classifyStageDevice(viewportWidth: number, viewportHeight: number): StageDeviceState {
  const shortestSide = Math.min(viewportWidth, viewportHeight);
  if (shortestSide < 600) return "phone_unsupported";
  if (viewportHeight > viewportWidth) return "tablet_portrait";
  return "supported";
}
