<script setup lang="ts">
import { createTextVNode, defineComponent } from 'vue';
import { App as AntdvApp } from 'antdv-next';

defineOptions({
  name: 'AppProvider'
});

type NoticeOptions = Record<string, any>;

function normalizeDuration(duration?: number | false) {
  if (typeof duration === 'number' && duration > 100) {
    return duration / 1000;
  }

  return duration;
}

function normalizeNoticeOptions(options: NoticeOptions) {
  const { content, action, duration, ...rest } = options;

  return {
    ...rest,
    description: rest.description ?? content,
    duration: normalizeDuration(duration),
    actions: rest.actions ?? action?.()
  };
}

function createMessageApi(message: any) {
  function open(type: string, content: any, options?: NoticeOptions | number) {
    if (typeof options === 'object') {
      const { duration, onLeave, onClose, ...rest } = options;

      return message.open({
        ...rest,
        type,
        content,
        duration: normalizeDuration(duration),
        onClose: onClose ?? onLeave
      });
    }

    return message[type](content, normalizeDuration(options));
  }

  return {
    ...message,
    success: (content: any, options?: NoticeOptions | number) => open('success', content, options),
    error: (content: any, options?: NoticeOptions | number) => open('error', content, options),
    info: (content: any, options?: NoticeOptions | number) => open('info', content, options),
    warning: (content: any, options?: NoticeOptions | number) => open('warning', content, options),
    loading: (content: any, options?: NoticeOptions | number) => open('loading', content, options)
  };
}

function createDialogApi(modal: any) {
  function normalizeDialogOptions(options: NoticeOptions) {
    const { positiveText, negativeText, onPositiveClick, onNegativeClick, onClose, closeOnEsc, ...rest } = options;

    return {
      ...rest,
      okText: positiveText,
      cancelText: negativeText,
      keyboard: closeOnEsc,
      onOk: onPositiveClick,
      onCancel: onNegativeClick,
      afterClose: onClose
    };
  }

  function open(type: 'info' | 'success' | 'error' | 'warning', options: NoticeOptions) {
    const config = normalizeDialogOptions(options);

    if (options.negativeText) {
      return modal.confirm({ ...config, type });
    }

    return modal[type](config);
  }

  return {
    info: (options: NoticeOptions) => open('info', options),
    success: (options: NoticeOptions) => open('success', options),
    error: (options: NoticeOptions) => open('error', options),
    warning: (options: NoticeOptions) => open('warning', options)
  };
}

function createNotificationApi(notification: any) {
  function open(options: NoticeOptions) {
    const key = options.key ?? `notification-${Date.now()}`;

    notification.open({
      ...normalizeNoticeOptions(options),
      key
    });

    return {
      destroy: () => notification.destroy(key)
    };
  }

  return {
    ...notification,
    create: open,
    open,
    success: (options: NoticeOptions) => notification.success(normalizeNoticeOptions(options)),
    error: (options: NoticeOptions) => notification.error(normalizeNoticeOptions(options)),
    info: (options: NoticeOptions) => notification.info(normalizeNoticeOptions(options)),
    warning: (options: NoticeOptions) => notification.warning(normalizeNoticeOptions(options))
  };
}

const ContextHolder = defineComponent({
  name: 'ContextHolder',
  setup() {
    const { message, modal, notification } = AntdvApp.useApp();

    function register() {
      window.$dialog = createDialogApi(modal);
      window.$message = createMessageApi(message);
      window.$notification = createNotificationApi(notification);
    }

    register();

    return () => createTextVNode();
  }
});
</script>

<template>
  <AApp class="h-full">
    <ContextHolder />
    <slot></slot>
  </AApp>
</template>

<style scoped></style>
