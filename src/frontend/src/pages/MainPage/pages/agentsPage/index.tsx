import { useCallback, useState } from "react";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import PaginatorComponent from "@/components/common/paginatorComponent";
import CardsWrapComponent from "@/components/core/cardsWrapComponent";
import { useGetPublicFlowsQuery } from "@/controllers/API/queries/flows/use-get-public-flows";
import AgentCard from "./components/agent-card";
import ListSkeleton from "../../components/listSkeleton";

const AgentsPage = () => {
  const [pageIndex, setPageIndex] = useState(1);
  const [pageSize, setPageSize] = useState(12);

  const { data, isLoading } = useGetPublicFlowsQuery({
    page: pageIndex,
    size: pageSize,
  });

  const handlePageChange = useCallback(
    (newPageIndex: number, newPageSize: number) => {
      setPageIndex(newPageIndex);
      setPageSize(newPageSize);
    },
    [],
  );

  const flows = data?.items ?? [];
  const pagination = {
    page: data?.page ?? 1,
    size: data?.size ?? 12,
    total: data?.total ?? 0,
    pages: data?.pages ?? 0,
  };

  const isEmpty = !isLoading && flows.length === 0;

  return (
    <CardsWrapComponent>
      <div
        className="flex h-full w-full flex-col overflow-y-auto"
        data-testid="agents-wrapper"
      >
        <div className="flex h-full w-full flex-col 3xl:container">
          <div className="flex flex-1 flex-col justify-start p-4">
            <div className="mb-4">
              <h1 className="text-xl font-semibold">Agents</h1>
              <p className="text-sm text-muted-foreground">
                Browse all public agents
              </p>
            </div>

            {isLoading ? (
              <div className="flex flex-col gap-1">
                <ListSkeleton />
                <ListSkeleton />
              </div>
            ) : isEmpty ? (
              <div className="flex flex-1 flex-col items-center justify-center">
                <div className="flex flex-col items-center gap-4 text-center">
                  <ForwardedIconComponent
                    name="Bot"
                    className="h-16 w-16 text-muted-foreground"
                  />
                  <h2 className="text-xl font-semibold text-foreground">
                    No Public Agents Yet
                  </h2>
                  <p className="max-w-md text-sm text-muted-foreground">
                    Agents are AI assistants that can help you with various
                    tasks. There are no public agents available at the moment.
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex h-full flex-col">
                <div className="flex flex-col gap-1">
                  {flows.map((flow) => (
                    <AgentCard key={flow.id} flowData={flow} />
                  ))}
                </div>
              </div>
            )}
          </div>

          {!isLoading && !isEmpty && pagination.total >= 10 && (
            <div className="flex justify-end px-3 py-4">
              <PaginatorComponent
                pageIndex={pagination.page}
                pageSize={pagination.size}
                rowsCount={[12, 24, 48, 96]}
                totalRowsCount={pagination.total}
                paginate={handlePageChange}
                pages={pagination.pages}
              />
            </div>
          )}
        </div>
      </div>
    </CardsWrapComponent>
  );
};

export default AgentsPage;
