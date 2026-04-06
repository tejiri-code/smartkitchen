import { RecipeFeedback, ChatFeedback } from '../types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function submitRecipeFeedback(feedback: RecipeFeedback): Promise<{ status: string; recipe: string; rating: number }> {
  const response = await fetch(`${API_BASE}/feedback/recipe`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(feedback),
  });

  if (!response.ok) {
    throw new Error(`Failed to submit recipe feedback: ${response.statusText}`);
  }

  return response.json();
}

export async function submitChatFeedback(feedback: ChatFeedback): Promise<{ status: string; helpful: boolean }> {
  const response = await fetch(`${API_BASE}/feedback/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(feedback),
  });

  if (!response.ok) {
    throw new Error(`Failed to submit chat feedback: ${response.statusText}`);
  }

  return response.json();
}
