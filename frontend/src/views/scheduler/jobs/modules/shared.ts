import dayjs from 'dayjs';
import { $t } from '@/locales';

export function formatDateTime(value?: string | null) {
  if (!value) return '-';

  return dayjs(value).format('YYYY-MM-DD HH:mm:ss');
}

export function formatSeconds(value?: number | null) {
  if (value === null || value === undefined) return '-';

  return `${value}s`;
}

export function formatDuration(value?: number | null) {
  if (value === null || value === undefined) return '-';

  return `${value.toFixed(3)}s`;
}

export function formatJson(value: unknown) {
  if (value === null || value === undefined) return '-';

  return JSON.stringify(value, null, 2);
}

export function translateJobStatus(value: string) {
  const key = `page.scheduler.jobStatus.${value}`;
  const label = $t(key as App.I18n.I18nKey);

  return label === key ? value : label;
}

export function translateRunOutcome(value: string) {
  const key = `page.scheduler.runOutcome.${value}`;
  const label = $t(key as App.I18n.I18nKey);

  return label === key ? value : label;
}

export function getJobStatusTagColor(value: string) {
  const tagMap: Record<string, AntdvUI.ThemeColor> = {
    scheduled: 'primary',
    running: 'success',
    paused: 'warning',
    completed: 'default'
  };

  return tagMap[value] || 'default';
}

export function getRunOutcomeTagColor(value: string) {
  const tagMap: Record<string, AntdvUI.ThemeColor> = {
    success: 'success',
    error: 'error',
    missed_start_deadline: 'warning',
    cancelled: 'default'
  };

  return tagMap[value] || 'default';
}

export function formatBoolean(value?: boolean) {
  if (value === undefined) return '-';

  return value ? $t('common.yesOrNo.yes') : $t('common.yesOrNo.no');
}
