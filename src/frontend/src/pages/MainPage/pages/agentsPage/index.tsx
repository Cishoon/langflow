import ForwardedIconComponent from "@/components/common/genericIconComponent";
import CardsWrapComponent from "@/components/core/cardsWrapComponent";

const AgentsPage = () => {
  return (
    <CardsWrapComponent>
      <div
        className="flex h-full w-full flex-col overflow-y-auto"
        data-testid="agents-wrapper"
      >
        <div className="flex h-full w-full flex-col 3xl:container">
          <div className="flex flex-1 flex-col items-center justify-center p-4">
            <div className="flex flex-col items-center gap-4 text-center">
              <ForwardedIconComponent
                name="Bot"
                className="h-16 w-16 text-muted-foreground"
              />
              <h2 className="text-xl font-semibold text-foreground">
                No Agents Yet
              </h2>
              <p className="max-w-md text-sm text-muted-foreground">
                Agents are autonomous AI assistants that can help you with
                various tasks. Create your first agent to get started.
              </p>
            </div>
          </div>
        </div>
      </div>
    </CardsWrapComponent>
  );
};

export default AgentsPage;
