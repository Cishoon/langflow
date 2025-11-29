import { useLocation } from "react-router-dom";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { CustomStoreButton } from "@/customization/components/custom-store-button";
import {
  ENABLE_DATASTAX_LANGFLOW,
  ENABLE_FILE_MANAGEMENT,
  ENABLE_KNOWLEDGE_BASES,
} from "@/customization/feature-flags";
import { useCustomNavigate } from "@/customization/hooks/use-custom-navigate";
import { useIsMobile } from "@/hooks/use-mobile";

type SideBarFoldersButtonsComponentProps = {
  handleChangeFolder?: (id: string) => void;
  handleDeleteFolder?: (item: unknown) => void;
  handleFilesClick?: () => void;
};

const SideBarFoldersButtonsComponent = (
  _props: SideBarFoldersButtonsComponentProps,
) => {
  const location = useLocation();
  const pathname = location.pathname;
  const _navigate = useCustomNavigate();
  const isMobile = useIsMobile({ maxWidth: 1024 });

  const isFlowsPage =
    pathname.includes("/flows") ||
    pathname.includes("/all") ||
    pathname === "/" ||
    pathname.includes("/folder/");
  const isAgentsPage = pathname.includes("/agents");

  const handleFilesNavigation = () => {
    _navigate("/assets/files");
  };

  const handleKnowledgeNavigation = () => {
    _navigate("/assets/knowledge-bases");
  };

  return (
    <Sidebar
      collapsible={isMobile ? "offcanvas" : "none"}
      data-testid="project-sidebar"
    >
      <SidebarContent>
        <SidebarGroup className="p-4 py-2">
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton
                  size="md"
                  onClick={() => _navigate("/flows")}
                  isActive={isFlowsPage}
                  data-testid="sidebar-nav-flows"
                >
                  <ForwardedIconComponent name="Workflow" className="h-4 w-4" />
                  <span className="text-sm font-semibold">Flows</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton
                  size="md"
                  onClick={() => _navigate("/agents")}
                  isActive={isAgentsPage}
                  data-testid="sidebar-nav-agents"
                >
                  <ForwardedIconComponent name="Bot" className="h-4 w-4" />
                  <span className="text-sm font-semibold">Agents</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <div className="flex-1" />
      </SidebarContent>
      {ENABLE_FILE_MANAGEMENT && (
        <SidebarFooter className="border-t">
          <div className="grid w-full items-center gap-2 p-2">
            {ENABLE_DATASTAX_LANGFLOW && <CustomStoreButton />}
            {ENABLE_KNOWLEDGE_BASES && (
              <SidebarMenuButton
                onClick={handleKnowledgeNavigation}
                size="md"
                className="text-sm"
              >
                <ForwardedIconComponent name="Library" className="h-4 w-4" />
                Knowledge
              </SidebarMenuButton>
            )}
            <SidebarMenuButton
              onClick={handleFilesNavigation}
              size="md"
              className="text-sm"
            >
              <ForwardedIconComponent name="File" className="h-4 w-4" />
              My Files
            </SidebarMenuButton>
          </div>
        </SidebarFooter>
      )}
    </Sidebar>
  );
};

export default SideBarFoldersButtonsComponent;
