export {};

type GlobalMessageApi = Omit<
  import('antdv-next/dist/message/interface').MessageInstance,
  'success' | 'error' | 'info' | 'warning' | 'loading'
> &
  Record<
    'success' | 'error' | 'info' | 'warning' | 'loading',
    (content: any, options?: number | Record<string, any>) => any
  >;

declare global {
  export interface Window {
    /** NProgress instance */
    NProgress?: import('nprogress').NProgress;
    /** Dialog instance */
    $dialog?: Record<'info' | 'success' | 'error' | 'warning', (options: Record<string, any>) => any>;
    /** Message instance */
    $message?: GlobalMessageApi;
    /** Notification instance */
    $notification?: import('antdv-next/dist/notification/interface').NotificationInstance & {
      create: (options: Record<string, any>) => { destroy: () => void };
    };
  }

  /** Build time of the project */
  export const BUILD_TIME: string;
}
