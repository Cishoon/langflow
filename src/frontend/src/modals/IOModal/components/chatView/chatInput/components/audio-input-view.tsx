import type React from "react";
import { useRef, useState } from "react";
import ShortUniqueId from "short-unique-id";
import IconComponent from "../../../../../../components/common/genericIconComponent";
import { Button } from "@/components/ui/button";
import Loading from "@/components/ui/loading";
import { usePostUploadFile } from "@/controllers/API/queries/files/use-post-upload-file";
import useAlertStore from "@/stores/alertStore";
import useFlowsManagerStore from "@/stores/flowsManagerStore";
import type { FilePreviewType } from "../../../../../../types/components";

const ALLOWED_AUDIO_EXTENSIONS = [
  "mp3",
  "wav",
  "flac",
  "m4a",
  "ogg",
  "aac",
  "wma",
  "opus",
  "webm",
  "amr",
];

interface AudioInputViewProps {
  isBuilding: boolean;
  sendMessage: (args: { repeat: number; files?: string[] }) => Promise<void>;
  stopBuilding: () => void;
  files: FilePreviewType[];
  setFiles: (
    files: FilePreviewType[] | ((prev: FilePreviewType[]) => FilePreviewType[]),
  ) => void;
}

const AudioInputView: React.FC<AudioInputViewProps> = ({
  isBuilding,
  sendMessage,
  stopBuilding,
  files,
  setFiles,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const setErrorData = useAlertStore((state) => state.setErrorData);
  const currentFlowId = useFlowsManagerStore((state) => state.currentFlowId);
  const { mutate } = usePostUploadFile();
  const [uploadedFile, setUploadedFile] = useState<FilePreviewType | null>(
    null,
  );

  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const fileExtension = file.name.split(".").pop()?.toLowerCase();
    if (!fileExtension || !ALLOWED_AUDIO_EXTENSIONS.includes(fileExtension)) {
      setErrorData({
        title: "Invalid audio file",
        list: [
          "Please upload a valid audio file.",
          `Supported formats: ${ALLOWED_AUDIO_EXTENSIONS.join(", ")}`,
        ],
      });
      return;
    }

    const uid = new ShortUniqueId();
    const id = uid.randomUUID(10);

    const newFile: FilePreviewType = {
      file,
      loading: true,
      error: false,
      id,
      type: "audio",
    };

    setUploadedFile(newFile);
    setFiles([newFile]);

    mutate(
      { file, id: currentFlowId },
      {
        onSuccess: (data) => {
          const updatedFile = {
            ...newFile,
            loading: false,
            path: data.file_path,
          };
          setUploadedFile(updatedFile);
          setFiles([updatedFile]);
        },
        onError: (error) => {
          const errorFile = { ...newFile, loading: false, error: true };
          setUploadedFile(errorFile);
          setFiles([errorFile]);
          setErrorData({
            title: "Error uploading audio file",
            list: [error.response?.data?.detail || "Upload failed"],
          });
        },
      },
    );

    event.target.value = "";
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleSend = async () => {
    if (!uploadedFile?.path) return;
    await sendMessage({
      repeat: 1,
      files: [uploadedFile.path],
    });
    setUploadedFile(null);
    setFiles([]);
  };

  const handleRemoveFile = () => {
    setUploadedFile(null);
    setFiles([]);
  };

  return (
    <div className="flex h-full w-full flex-col items-center justify-center">
      <div className="flex w-full flex-col items-center justify-center gap-3 rounded-md border border-input bg-muted p-4">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept={ALLOWED_AUDIO_EXTENSIONS.map((ext) => `.${ext}`).join(",")}
          className="hidden"
        />

        {!uploadedFile ? (
          <>
            <Button
              variant="outline"
              className="flex items-center gap-2"
              onClick={handleButtonClick}
              disabled={isBuilding}
            >
              <IconComponent name="Upload" className="h-4 w-4" />
              Upload Audio File
            </Button>
            <p className="text-sm text-muted-foreground">
              Supported formats: {ALLOWED_AUDIO_EXTENSIONS.join(", ")}
            </p>
          </>
        ) : (
          <div className="flex w-full flex-col items-center gap-3">
            <div className="flex items-center gap-2 rounded-md bg-background px-3 py-2">
              <IconComponent name="FileAudio" className="h-5 w-5" />
              <span className="max-w-[200px] truncate text-sm">
                {uploadedFile.file?.name}
              </span>
              {uploadedFile.loading ? (
                <Loading className="h-4 w-4" />
              ) : uploadedFile.error ? (
                <IconComponent
                  name="AlertCircle"
                  className="h-4 w-4 text-destructive"
                />
              ) : (
                <IconComponent
                  name="CheckCircle"
                  className="h-4 w-4 text-success"
                />
              )}
              {!uploadedFile.loading && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={handleRemoveFile}
                >
                  <IconComponent name="X" className="h-3 w-3" />
                </Button>
              )}
            </div>

            {!isBuilding ? (
              <Button
                className="font-semibold"
                onClick={handleSend}
                disabled={
                  uploadedFile.loading || uploadedFile.error || !uploadedFile.path
                }
              >
                <IconComponent name="Play" className="mr-2 h-4 w-4" />
                Run Flow
              </Button>
            ) : (
              <Button
                onClick={stopBuilding}
                variant="outline"
                className="flex items-center gap-2"
              >
                Stop
                <Loading className="h-4 w-4" />
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AudioInputView;
