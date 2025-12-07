import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useGetDownloadFileMutation } from "@/controllers/API/queries/files";
import { ForwardedIconComponent } from "../../../../../../components/common/genericIconComponent";
import { BASE_URL_API } from "../../../../../../constants/constants";
import type { fileCardPropsType } from "../../../../../../types/components";
import formatFileName from "../utils/format-file-name";
import getClasses from "../utils/get-classes";
import DownloadButton from "./download-button";

const imgTypes = new Set(["png", "jpg", "jpeg", "gif", "webp", "image"]);
const audioTypes = new Set([
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
  "audio",
]);

export default function FileCard({
  fileName,
  path,
  fileType,
  showFile = true,
}: fileCardPropsType): JSX.Element | undefined {
  // Normalize path/name/type; support remote URLs with query strings
  let name = "";
  let type = "";
  let pathString = "";
  if (typeof path === "string") {
    pathString = path;
    const urlPart = path.split("?")[0] || path;
    name = urlPart.split("/").pop() || "";
    type = urlPart.split(".").pop() || "";
  } else {
    pathString = path.path;
    const urlPart = path.path.split("?")[0] || path.path;
    name = path.name || urlPart.split("/").pop() || "";
    type = path.type || urlPart.split(".").pop() || "";
  }

  const [isHovered, setIsHovered] = useState(false);
  const { mutate } = useGetDownloadFileMutation({
    filename: name || fileName,
    path: pathString,
  });
  function handleMouseEnter(): void {
    setIsHovered(true);
  }
  function handleMouseLeave(): void {
    setIsHovered(false);
  }

  const fileWrapperClasses = getClasses(isHovered);

  const isRemote =
    typeof pathString === "string" && pathString.startsWith("http");
  const imgSrc = isRemote
    ? pathString
    : `${BASE_URL_API}files/images/${pathString}`;
  const audioSrc = isRemote
    ? pathString
    : `${BASE_URL_API}files/download/${pathString}`;
  const normalizedType = (type || fileType || "").toLowerCase();

  if (showFile) {
    if (audioTypes.has(normalizedType) || normalizedType.startsWith("audio")) {
      return (
        <div
          className="inline-block w-full rounded-lg transition-all"
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
          <div className="flex w-full items-center gap-3 rounded-lg border border-border p-3">
            <ForwardedIconComponent name="Waveform" className="h-8 w-8" />
            <div className="flex w-full flex-col gap-2">
              <span className="font-bold">{formatFileName(fileName, 40)}</span>
              <audio controls className="w-full" src={audioSrc} />
            </div>
            {!isRemote && (
              <DownloadButton
                isHovered={isHovered}
                handleDownload={() => mutate(undefined)}
              />
            )}
          </div>
        </div>
      );
    }

    if (imgTypes.has(normalizedType) || normalizedType.startsWith("image")) {
      return (
        <div
          className="inline-block w-full rounded-lg transition-all"
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
          style={{ display: "inline-block" }}
        >
          <div className="relative w-[50%] rounded-lg border border-border">
            <img
              src={imgSrc}
              alt="generated image"
              className="m-0 h-auto w-auto rounded-lg border border-border p-0 transition-all"
            />
            {!isRemote && (
              <DownloadButton
                isHovered={isHovered}
                handleDownload={() => mutate(undefined)}
              />
            )}
            {isRemote && (
              <div className="absolute right-2 top-2">
                <Button
                  size="icon"
                  variant="secondary"
                  onClick={() =>
                    window.open(imgSrc, "_blank", "noopener,noreferrer")
                  }
                >
                  <ForwardedIconComponent name="Download" className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>
        </div>
      );
    }

    return (
      <div
        className={fileWrapperClasses}
        onClick={() => mutate(undefined)}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        <div className="ml-3 flex h-full w-full items-center gap-2 text-sm">
          <ForwardedIconComponent name="File" className="h-8 w-8" />
          <div className="flex flex-col">
            <span className="font-bold">{formatFileName(fileName, 20)}</span>
            <span>File</span>
          </div>
        </div>
        <DownloadButton
          isHovered={isHovered}
          handleDownload={() => mutate(undefined)}
        />
      </div>
    );
  }
  return undefined;
}
