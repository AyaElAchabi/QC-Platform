"use client";

import { ReactNode } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LucideIcon } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

// Types
interface StatsCardProps {
    title: string;
    value: string | number;
    icon: LucideIcon;
    description?: string;
    href?: string;
    trend?: {
        value: number;
        isPositive: boolean;
    };
    color?: string;
}

interface QuickActionCardProps {
    title: string;
    description: string;
    icon: LucideIcon;
    onClick?: () => void;
    href?: string;
    variant?: "default" | "outline" | "secondary";
}

interface RecentActivityItemProps {
    title: string;
    description: string;
    time: string;
    icon?: LucideIcon;
    href?: string;
}

interface ProjectOverviewCardProps {
    project: {
        id: string;
        name: string;
        description?: string;
        total_images?: number;
        annotated_images?: number;
        models_count?: number;
        status?: string;
    };
}

interface DashboardSectionProps {
    title: string;
    description?: string;
    children: ReactNode;
    action?: {
        label: string;
        href?: string;
        onClick?: () => void;
    };
}

/**
 * Carte de statistique avec icône, titre, valeur et optionnellement un trend
 */
export function StatsCard({
    title,
    value,
    icon: Icon,
    description,
    href,
    trend,
    color = "text-blue-600"
}: StatsCardProps) {
    const CardWrapper = ({ children }: { children: ReactNode }) =>
        href ? (
            <Link href={href}>
                <Card className="hover:shadow-lg transition cursor-pointer">
                    {children}
                </Card>
            </Link>
        ) : (
            <Card>{children}</Card>
        );

    return (
        <CardWrapper>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                    {title}
                </CardTitle>
                <Icon className={cn("h-4 w-4", color)} />
            </CardHeader>
            <CardContent>
                <div className="text-3xl font-bold">{value}</div>
                {description && (
                    <p className="text-xs text-muted-foreground mt-1">{description}</p>
                )}
                {trend && (
                    <div className="flex items-center mt-2 text-xs">
                        <span
                            className={cn(
                                "font-medium",
                                trend.isPositive ? "text-green-600" : "text-red-600"
                            )}
                        >
                            {trend.isPositive ? "+" : ""}
                            {trend.value}%
                        </span>
                        <span className="text-muted-foreground ml-1">vs dernier mois</span>
                    </div>
                )}
            </CardContent>
        </CardWrapper>
    );
}

/**
 * Carte d'action rapide avec bouton
 */
export function QuickActionCard({
    title,
    description,
    icon: Icon,
    onClick,
    href,
    variant = "default"
}: QuickActionCardProps) {
    const content = (
        <Card className="hover:shadow-md transition cursor-pointer">
            <CardHeader>
                <div className="flex items-center space-x-3">
                    <div className={cn(
                        "p-2 rounded-lg",
                        variant === "default" ? "bg-blue-100" : "bg-gray-100"
                    )}>
                        <Icon className={cn(
                            "h-5 w-5",
                            variant === "default" ? "text-blue-600" : "text-gray-600"
                        )} />
                    </div>
                    <div>
                        <CardTitle className="text-base">{title}</CardTitle>
                        <CardDescription className="text-sm">{description}</CardDescription>
                    </div>
                </div>
            </CardHeader>
        </Card>
    );

    if (href) {
        return <Link href={href}>{content}</Link>;
    }

    return <div onClick={onClick}>{content}</div>;
}

/**
 * Item d'activité récente
 */
export function RecentActivityItem({
    title,
    description,
    time,
    icon: Icon,
    href
}: RecentActivityItemProps) {
    const content = (
        <div className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition">
            {Icon && (
                <div className="p-2 bg-gray-100 rounded-lg mt-1">
                    <Icon className="h-4 w-4 text-gray-600" />
                </div>
            )}
            <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{title}</p>
                <p className="text-sm text-gray-500 truncate">{description}</p>
            </div>
            <span className="text-xs text-gray-400 whitespace-nowrap">{time}</span>
        </div>
    );

    if (href) {
        return <Link href={href}>{content}</Link>;
    }

    return content;
}

/**
 * Carte d'aperçu de projet avec progression
 */
export function ProjectOverviewCard({ project }: ProjectOverviewCardProps) {
    const progress = project.total_images
        ? Math.round(((project.annotated_images || 0) / project.total_images) * 100)
        : 0;

    return (
        <Link href={`/projects/${project.id}`}>
            <Card className="hover:shadow-lg transition cursor-pointer">
                <CardHeader>
                    <div className="flex justify-between items-start">
                        <div className="flex-1">
                            <CardTitle className="text-lg">{project.name}</CardTitle>
                            {project.description && (
                                <CardDescription className="mt-1 line-clamp-2">
                                    {project.description}
                                </CardDescription>
                            )}
                        </div>
                        {project.status && (
                            <span
                                className={cn(
                                    "px-2 py-1 text-xs font-medium rounded-full",
                                    project.status === "active"
                                        ? "bg-green-100 text-green-800"
                                        : "bg-gray-100 text-gray-800"
                                )}
                            >
                                {project.status === "active" ? "Actif" : "Inactif"}
                            </span>
                        )}
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-3 gap-4 mb-3">
                        <div>
                            <p className="text-xs text-muted-foreground">Images</p>
                            <p className="text-lg font-semibold">{project.total_images || 0}</p>
                        </div>
                        <div>
                            <p className="text-xs text-muted-foreground">Annoté</p>
                            <p className="text-lg font-semibold">{project.annotated_images || 0}</p>
                        </div>
                        <div>
                            <p className="text-xs text-muted-foreground">Modèles</p>
                            <p className="text-lg font-semibold">{project.models_count || 0}</p>
                        </div>
                    </div>
                    {project.total_images && project.total_images > 0 && (
                        <div>
                            <div className="flex justify-between text-xs text-muted-foreground mb-1">
                                <span>Progression</span>
                                <span>{progress}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                    className="bg-blue-600 h-2 rounded-full transition-all"
                                    style={{ width: `${progress}%` }}
                                />
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>
        </Link>
    );
}

/**
 * Section de dashboard avec titre et action optionnelle
 */
export function DashboardSection({
    title,
    description,
    children,
    action
}: DashboardSectionProps) {
    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold">{title}</h2>
                    {description && (
                        <p className="text-muted-foreground text-sm">{description}</p>
                    )}
                </div>
                {action && (
                    action.href ? (
                        <Link href={action.href}>
                            <Button>{action.label}</Button>
                        </Link>
                    ) : (
                        <Button onClick={action.onClick}>{action.label}</Button>
                    )
                )}
            </div>
            {children}
        </div>
    );
}
