'use client';

import { cn } from '@/lib/utils';
import { HTMLAttributes, forwardRef } from 'react';

const Table = forwardRef<HTMLTableElement, HTMLAttributes<HTMLTableElement>>(
  ({ className, ...props }, ref) => {
    return (
      <div className="overflow-x-auto">
        <table
          ref={ref}
          className={cn('min-w-full divide-y divide-gray-200', className)}
          {...props}
        />
      </div>
    );
  }
);
Table.displayName = 'Table';

const TableHeader = forwardRef<HTMLTableSectionElement, HTMLAttributes<HTMLTableSectionElement>>(
  ({ className, ...props }, ref) => {
    return (
      <thead
        ref={ref}
        className={cn('bg-gray-50', className)}
        {...props}
      />
    );
  }
);
TableHeader.displayName = 'TableHeader';

const TableBody = forwardRef<HTMLTableSectionElement, HTMLAttributes<HTMLTableSectionElement>>(
  ({ className, ...props }, ref) => {
    return (
      <tbody
        ref={ref}
        className={cn('bg-white divide-y divide-gray-200', className)}
        {...props}
      />
    );
  }
);
TableBody.displayName = 'TableBody';

const TableRow = forwardRef<HTMLTableRowElement, HTMLAttributes<HTMLTableRowElement>>(
  ({ className, ...props }, ref) => {
    return (
      <tr
        ref={ref}
        className={cn('hover:bg-gray-50 transition-colors', className)}
        {...props}
      />
    );
  }
);
TableRow.displayName = 'TableRow';

const TableHead = forwardRef<HTMLTableCellElement, HTMLAttributes<HTMLTableCellElement>>(
  ({ className, ...props }, ref) => {
    return (
      <th
        ref={ref}
        className={cn(
          'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
          className
        )}
        {...props}
      />
    );
  }
);
TableHead.displayName = 'TableHead';

const TableCell = forwardRef<HTMLTableCellElement, HTMLAttributes<HTMLTableCellElement>>(
  ({ className, ...props }, ref) => {
    return (
      <td
        ref={ref}
        className={cn('px-6 py-4 whitespace-nowrap text-sm', className)}
        {...props}
      />
    );
  }
);
TableCell.displayName = 'TableCell';

export { Table, TableHeader, TableBody, TableRow, TableHead, TableCell };
