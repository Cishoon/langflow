import { useEffect, useState } from "react";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import { Card } from "@/components/ui/card";
import type { FlowType } from "@/types/flow";
import { swatchColors } from "@/utils/styleUtils";
import { getNumberFromString } from "@/utils/utils";
import { useGetTemplateStyle } from "../../../utils/get-template-style";
import { timeElapsed } from "../../../utils/time-elapse";

const AgentCard = ({ flowData }: { flowData: FlowType }) => {
  const { getIcon } = useGetTemplateStyle(flowData);
  const [icon, setIcon] = useState<string>("");

  useEffect(() => {
    getIcon().then(setIcon);
  }, [getIcon]);

  const swatchIndex =
    (flowData.gradient && !isNaN(parseInt(flowData.gradient))
      ? parseInt(flowData.gradient)
      : getNumberFromString(flowData.gradient ?? flowData.id)) %
    swatchColors.length;

  const handleClick = () => {
    // Open playground in new tab
    window.open(`/playground/${flowData.id}`, "_blank");
  };

  return (
    <Card
      onClick={handleClick}
      className="flex cursor-pointer flex-row bg-background justify-between rounded-lg border-none px-4 py-3 shadow-none hover:bg-muted"
      data-testid="agent-card"
    >
      <div className="flex min-w-0 items-center gap-4">
        <div
          className={`flex items-center justify-center rounded-lg p-1.5 ${swatchColors[swatchIndex]}`}
        >
          <ForwardedIconComponent
            name={flowData?.icon || icon || "Bot"}
            aria-hidden="true"
            className="flex h-5 w-5 items-center justify-center"
          />
        </div>

        <div className="flex min-w-0 flex-col justify-start">
          <div className="flex min-w-0 flex-wrap items-baseline gap-x-2 gap-y-1">
            <div className="flex min-w-0 flex-shrink truncate text-sm font-semibold">
              <span className="truncate" data-testid={`agent-name-${flowData.id}`}>
                {flowData.name}
              </span>
            </div>
            <div className="flex min-w-0 flex-shrink text-xs text-muted-foreground">
              <span className="truncate">
                Edited {timeElapsed(flowData.updated_at)} ago
              </span>
            </div>
          </div>
          {flowData.description && (
            <p className="mt-1 truncate text-xs text-muted-foreground">
              {flowData.description}
            </p>
          )}
        </div>
      </div>

      <div className="ml-5 flex items-center">
        <ForwardedIconComponent
          name="Play"
          aria-hidden="true"
          className="h-5 w-5 text-muted-foreground"
        />
      </div>
    </Card>
  );
};

export default AgentCard;
