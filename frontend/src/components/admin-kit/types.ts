import type { Component, VNodeChild } from 'vue'
import type { TableColumnsType, TablePaginationConfig, TableProps } from 'antdv-next'

export type AdminMenuIcon = Component | (() => VNodeChild)
export type AdminMenuTheme = 'light' | 'dark'
export type AdminSearchFieldType = 'input' | 'select' | 'dateRange' | 'number' | 'custom'
export type AdminSearchFieldValue = string | number | boolean | null | undefined | unknown[]

export interface AdminMenuItem {
  key: string
  path?: string
  label: string
  hint?: string
  icon?: AdminMenuIcon
  children?: AdminMenuItem[]
  danger?: boolean
}

export interface AdminLoginPayload {
  username: string
  password: string
  captcha?: string
}

export interface AdminLoginHighlight {
  icon?: Component
  title: string
  note: string
}

export interface AdminSearchFieldOption {
  label: string
  value: string | number | null
  disabled?: boolean
}

export interface AdminSearchField {
  key: string
  label: string
  type: AdminSearchFieldType
  placeholder?: string | [string, string]
  options?: AdminSearchFieldOption[]
  clearable?: boolean
  disabled?: boolean
  hidden?: boolean
  defaultValue?: any
  colProps?: Record<string, any>
  componentProps?: Record<string, any>
  formItemProps?: Record<string, any>
  showSearch?: boolean
}

export interface AdminDataTableProps<RecordType = Record<string, any>> {
  title?: string
  description?: string
  columns?: TableColumnsType<RecordType>
  dataSource?: RecordType[]
  rowKey?: TableProps<RecordType>['rowKey']
  loading?: TableProps<RecordType>['loading']
  size?: TableProps<RecordType>['size']
  scroll?: TableProps<RecordType>['scroll']
  scrollX?: TableProps<RecordType>['scroll'] extends infer Scroll
    ? Scroll extends { x?: infer X }
      ? X
      : string | number | true
    : string | number | true
  scrollY?: TableProps<RecordType>['scroll'] extends infer Scroll
    ? Scroll extends { y?: infer Y }
      ? Y
      : string | number
    : string | number
  pagination?: false | TablePaginationConfig
  bordered?: boolean
  showHeader?: boolean
  sticky?: TableProps<RecordType>['sticky']
  tableLayout?: TableProps<RecordType>['tableLayout']
  emptyText?: string
  fill?: boolean
}
