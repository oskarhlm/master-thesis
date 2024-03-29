import { ChatElement, MessageSource } from './types';
import { createStore } from 'solid-js/store';

export const [chatElements, setChatElements] = createStore<ChatElement[]>([
  { type: 'agentSelector', agentType: 'sql' } satisfies ChatElement,
]);

function createUniqueId(): string {
  return `id-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}

export function addChatMessage(
  message: string,
  source: MessageSource,
  id?: string
) {
  setChatElements([
    ...chatElements.filter((el) => el.type !== 'spinner'),
    {
      type: 'messageGroupHeader',
      source: source,
    },
    {
      type: 'message',
      id: id || createUniqueId(),
      source: source,
      message: message,
    },
    {
      type: 'spinner',
    },
  ] satisfies ChatElement[]);
}

export function addStreamingChatMessage(
  source: MessageSource,
  callback?: () => void
) {
  let messageId = createUniqueId();

  return (nextToken: string | undefined, messageEnd?: boolean) => {
    if (nextToken) {
      if (
        !chatElements.find((el) => el.type === 'message' && el.id === messageId)
      ) {
        addChatMessage('', source, messageId);
      }

      setChatElements(
        (el) => {
          return el.type === 'message' && el.id === messageId;
        },
        'message' as any,
        (msg) => msg + nextToken
      );
    }

    if (messageEnd) {
      messageId = createUniqueId();
    }

    callback && callback();
  };
}
