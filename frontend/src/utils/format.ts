export const getErrorMessage = (error: unknown, fallback = '操作失败') =>
  error instanceof Error && error.message ? error.message : fallback

export const formatDateTime = (value?: string | null) => {
  if (!value) return '-'
  const date = new Date(value.replace(' ', 'T'))
  if (Number.isNaN(date.getTime())) return '-'
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}
