import type React from "react";
import { forwardRef } from "react";
import QwenSVG from "./QwenIcon";

export const QwenIcon = forwardRef<SVGSVGElement, React.PropsWithChildren<{}>>(
  (props, ref) => {
    return <QwenSVG ref={ref} {...props} />;
  },
);
