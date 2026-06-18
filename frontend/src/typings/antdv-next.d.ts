declare namespace AntdvUI {
  type ThemeColor = 'default' | 'error' | 'primary' | 'info' | 'success' | 'warning';
  type Align = 'start' | 'end' | 'center' | 'baseline';

  type TableColumnBase<T> = import('antdv-next').TableColumnType<T>;
  type TableColumnCheck = import('@sa/hooks').TableColumnCheck;
  type TableColumnFixed = import('@sa/hooks').TableColumnCheck['fixed'];

  type SetTableColumnKey<C, T> = Omit<C, 'key'> & { key: keyof T | (string & {}) };

  type TableColumnWithKey<T> = SetTableColumnKey<TableColumnBase<T>, T>;

  type TableColumn<T> = TableColumnWithKey<T> | TableColumnBase<T>;

  /**
   * the type of table operation
   *
   * - add: add table item
   * - edit: edit table item
   */
  type TableOperateType = 'add' | 'edit';
}
