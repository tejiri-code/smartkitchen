import { post } from "./client";
import type { AskRequest, AskResponse } from "@/lib/types";

export function askAssistant(req: AskRequest): Promise<AskResponse> {
  return post<AskResponse>("/assistant/ask", req);
}
