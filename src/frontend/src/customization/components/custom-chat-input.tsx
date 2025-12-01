import ChatInput from "@/modals/IOModal/components/chatView/chatInput/chat-input";
import type { ChatInputType } from "@/types/components";

export const CustomChatInput = ({
  sendMessage,
  inputRef,
  noInput,
  audioOnly,
  files,
  setFiles,
  isDragging,
  playgroundPage,
}: ChatInputType) => {
  return (
    <ChatInput
      sendMessage={sendMessage}
      inputRef={inputRef}
      noInput={noInput}
      audioOnly={audioOnly}
      files={files}
      setFiles={setFiles}
      isDragging={isDragging}
      playgroundPage={playgroundPage}
    />
  );
};

export default CustomChatInput;
