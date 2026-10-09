// apps/frontend/web/components/dashboard/DashboardGrid.tsx

import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface DashboardGridProps {
  children: ReactNode;
  className?: string;
  columns?: {
    default?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
    "2xl"?: number;
  };
  gap?: number | string;
  as?: keyof HTMLElementTagNameMap;
}

export function DashboardGrid({
  children,
  className,
  columns = {
    default: 1,
    sm: 2,
    md: 2,
    lg: 4,
    xl: 4,
  },
  gap = 4,
  as: Component = "div",
}: DashboardGridProps) {
  const getGridCols = () => {
    const cols: string[] = [];

    if (columns.default) cols.push(`grid-cols-${columns.default}`);
    if (columns.sm) cols.push(`sm:grid-cols-${columns.sm}`);
    if (columns.md) cols.push(`md:grid-cols-${columns.md}`);
    if (columns.lg) cols.push(`lg:grid-cols-${columns.lg}`);
    if (columns.xl) cols.push(`xl:grid-cols-${columns.xl}`);
    if (columns["2xl"]) cols.push(`2xl:grid-cols-${columns["2xl"]}`);

    return cols.join(" ");
  };

  const getGap = () => {
    if (typeof gap === "number") {
      return `gap-${gap}`;
    }

    return gap;
  };

  return (
    <Component
      className={cn(
        "grid auto-rows-fr",
        getGridCols(),
        getGap(),
        className
      )}
    >
      {children}
    </Component>
  );
}

// ============================================================
// Dashboard Grid Item
// ============================================================

interface DashboardGridItemProps {
  children: ReactNode;
  className?: string;
  colSpan?: {
    default?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
    "2xl"?: number;
  };
  rowSpan?: {
    default?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
    "2xl"?: number;
  };
}

export function DashboardGridItem({
  children,
  className,
  colSpan,
  rowSpan,
}: DashboardGridItemProps) {
  const getColSpan = () => {
    if (!colSpan) return "";

    const spans: string[] = [];

    if (colSpan.default) spans.push(`col-span-${colSpan.default}`);
    if (colSpan.sm) spans.push(`sm:col-span-${colSpan.sm}`);
    if (colSpan.md) spans.push(`md:col-span-${colSpan.md}`);
    if (colSpan.lg) spans.push(`lg:col-span-${colSpan.lg}`);
    if (colSpan.xl) spans.push(`xl:col-span-${colSpan.xl}`);
    if (colSpan["2xl"]) spans.push(`2xl:col-span-${colSpan["2xl"]}`);

    return spans.join(" ");
  };

  const getRowSpan = () => {
    if (!rowSpan) return "";

    const spans: string[] = [];

    if (rowSpan.default) spans.push(`row-span-${rowSpan.default}`);
    if (rowSpan.sm) spans.push(`sm:row-span-${rowSpan.sm}`);
    if (rowSpan.md) spans.push(`md:row-span-${rowSpan.md}`);
    if (rowSpan.lg) spans.push(`lg:row-span-${rowSpan.lg}`);
    if (rowSpan.xl) spans.push(`xl:row-span-${rowSpan.xl}`);
    if (rowSpan["2xl"]) spans.push(`2xl:row-span-${rowSpan["2xl"]}`);

    return spans.join(" ");
  };

  return (
    <div
      className={cn(
        "transition-all duration-300",
        getColSpan(),
        getRowSpan(),
        className
      )}
    >
      {children}
    </div>
  );
}