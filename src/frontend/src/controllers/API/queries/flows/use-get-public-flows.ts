import type { useQueryFunctionType } from "@/types/api";
import type { FlowType } from "@/types/flow";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";

interface PublicFlowsParams {
  page?: number;
  size?: number;
}

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export const useGetPublicFlowsQuery: useQueryFunctionType<
  PublicFlowsParams,
  PaginatedResponse<FlowType>
> = (params, options) => {
  const { query } = UseRequestProcessor();

  const getPublicFlowsFn = async () => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append("page", params.page.toString());
    if (params?.size) queryParams.append("size", params.size.toString());

    const url = `${getURL("FLOWS")}/public/${queryParams.toString() ? `?${queryParams.toString()}` : ""}`;
    return await api.get<PaginatedResponse<FlowType>>(url);
  };

  const responseFn = async () => {
    const { data } = await getPublicFlowsFn();
    return data;
  };

  const queryResult = query(
    ["useGetPublicFlowsQuery", params?.page, params?.size],
    responseFn,
    {
      ...options,
    },
  );

  return queryResult;
};
