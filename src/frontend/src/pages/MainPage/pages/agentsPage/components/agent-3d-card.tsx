import { useEffect, useRef, useState } from "react";
import { motion, useMotionTemplate, useMotionValue, useSpring } from "framer-motion";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import type { FlowType } from "@/types/flow";
import { swatchColors } from "@/utils/styleUtils";
import { getNumberFromString } from "@/utils/utils";
import { useGetTemplateStyle } from "../../../utils/get-template-style";
import { timeElapsed } from "../../../utils/time-elapse";
import { cn } from "@/utils/utils";

const ROTATION_RANGE = 20; // Maximum rotation angle in degrees
const HALF_ROTATION_RANGE = ROTATION_RANGE / 2;

const Agent3DCard = ({ flowData }: { flowData: FlowType }) => {
  const { getIcon } = useGetTemplateStyle(flowData);
  const [icon, setIcon] = useState<string>("");

  useEffect(() => {
    getIcon().then(setIcon);
  }, [getIcon]);

  const swatchIndex =
    (flowData.gradient && !isNaN(parseInt(flowData.gradient)) ? parseInt(flowData.gradient) : getNumberFromString(flowData.gradient ?? flowData.id)) %
    swatchColors.length;

  const ref = useRef<HTMLDivElement>(null);

  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const xSpring = useSpring(x, { stiffness: 300, damping: 30 });
  const ySpring = useSpring(y, { stiffness: 300, damping: 30 });

  const transform = useMotionTemplate`rotateX(${xSpring}deg) rotateY(${ySpring}deg)`;

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  const handleClick = () => {
    window.open(`/playground/${flowData.id}`, "_blank");
  };

  // Spotlight effect
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  function handleMouseMove({ currentTarget, clientX, clientY }: React.MouseEvent<HTMLDivElement>) {
    const { left, top, width, height } = currentTarget.getBoundingClientRect();

    // Spotlight
    mouseX.set(clientX - left);
    mouseY.set(clientY - top);

    // Rotation
    const rotMouseX = (clientX - left) * ROTATION_RANGE;
    const rotMouseY = (clientY - top) * ROTATION_RANGE;

    const rX = (rotMouseY / height - HALF_ROTATION_RANGE) * -1;
    const rY = rotMouseX / width - HALF_ROTATION_RANGE;

    x.set(rX);
    y.set(rY);
  }

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onClick={handleClick}
      style={{
        transformStyle: "preserve-3d",
        transform,
      }}
      className="group relative h-full w-full cursor-pointer rounded-xl bg-background border border-border/50 transition-colors hover:border-border/80"
    >
      {/* Spotlight */}
      <motion.div
        className="pointer-events-none absolute -inset-px rounded-xl opacity-0 transition duration-300 group-hover:opacity-100"
        style={{
          background: useMotionTemplate`
            radial-gradient(
              650px circle at ${mouseX}px ${mouseY}px,
              rgba(120, 120, 120, 0.15),
              transparent 80%
            )
          `,
        }}
      />

      <div className="relative flex h-full flex-col justify-between p-5" style={{ transform: "translateZ(20px)" }}>
        <div className="flex flex-col gap-4">
          <div className="flex items-start justify-between">
            <div className={cn("flex h-12 w-12 items-center justify-center rounded-xl shadow-sm ring-1 ring-inset ring-black/5", swatchColors[swatchIndex])}>
              <ForwardedIconComponent name={flowData?.icon || icon || "Bot"} aria-hidden="true" className="h-6 w-6 text-foreground" />
            </div>

            <div className="rounded-full bg-muted/50 px-2.5 py-0.5 text-xs font-medium text-muted-foreground">{timeElapsed(flowData.updated_at)}</div>
          </div>

          <div>
            <h3 className="font-semibold leading-none tracking-tight text-foreground group-hover:text-primary transition-colors">{flowData.name}</h3>
            {flowData.description && <p className="mt-2 line-clamp-2 text-sm text-muted-foreground">{flowData.description}</p>}
            {flowData.tags && flowData.tags.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1.5">
                {flowData.tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center rounded-md bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground ring-1 ring-inset ring-gray-500/10"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="mt-4 flex items-center justify-end">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="relative flex items-center justify-center rounded-full bg-primary/10 p-2 text-primary transition-colors hover:bg-primary hover:text-primary-foreground hover:shadow-[0_0_20px_rgba(var(--primary),0.5)]"
          >
            <ForwardedIconComponent name="Play" className="h-4 w-4" />
            <div className="absolute inset-0 -z-10 rounded-full bg-primary/20 blur-md opacity-0 transition-opacity group-hover:opacity-100" />
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
};

export default Agent3DCard;
