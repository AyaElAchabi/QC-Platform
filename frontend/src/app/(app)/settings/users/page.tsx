"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { userManagementApi } from "@/lib/api/users";
import { RoleBadge } from "@/components/auth/RoleBadge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { UserRole, ROLE_LABELS, ROLE_DESCRIPTIONS } from "@/types/roles";
import { Shield, UserX, UserCheck, Trash2, Search } from "lucide-react";
import { toast } from "sonner";
import { RequireAuth } from "@/components/auth/RequireAuth";

interface ChangeRoleDialogProps {
  isOpen: boolean;
  onClose: () => void;
  user: {
    id: string;
    email: string;
    role: UserRole;
  } | null;
}

function ChangeRoleDialog({ isOpen, onClose, user }: ChangeRoleDialogProps) {
  const [selectedRole, setSelectedRole] = useState<UserRole | "">("");
  const queryClient = useQueryClient();

  const changeRoleMutation = useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: UserRole }) =>
      userManagementApi.changeUserRole(userId, role),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast.success("Rôle modifié avec succès");
      onClose();
    },
    onError: (error: Error) => {
      toast.error(`Erreur: ${error.message}`);
    },
  });

  const handleSubmit = () => {
    if (user && selectedRole) {
      changeRoleMutation.mutate({ userId: user.id, role: selectedRole });
    }
  };

  useEffect(() => {
    if (user) {
      setSelectedRole(user.role);
    }
  }, [user]);

  if (!user) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Changer le rôle de l'utilisateur</DialogTitle>
          <DialogDescription>
            Utilisateur: {user.email}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div>
            <label className="text-sm font-medium mb-2 block">
              Rôle actuel
            </label>
            <RoleBadge role={user.role} />
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">
              Nouveau rôle
            </label>
            <Select
              value={selectedRole}
              onValueChange={(value) => setSelectedRole(value as UserRole)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Sélectionner un rôle" />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(ROLE_LABELS).map(([role, label]) => (
                  <SelectItem key={role} value={role}>
                    <div className="flex flex-col items-start">
                      <span className="font-medium">{label}</span>
                      <span className="text-xs text-gray-500">
                        {ROLE_DESCRIPTIONS[role as UserRole]}
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Annuler
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!selectedRole || selectedRole === user.role || changeRoleMutation.isPending}
          >
            {changeRoleMutation.isPending ? "Modification..." : "Confirmer"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default function UserManagementPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState<UserRole | "all">("all");
  const [selectedUser, setSelectedUser] = useState<{
    id: string;
    email: string;
    role: UserRole;
  } | null>(null);
  const [isRoleDialogOpen, setIsRoleDialogOpen] = useState(false);

  const queryClient = useQueryClient();

  // Récupérer la liste des utilisateurs
  const { data: usersData, isLoading } = useQuery({
    queryKey: ["users", roleFilter],
    queryFn: () =>
      userManagementApi.getUsers({
        role: roleFilter !== "all" ? roleFilter : undefined,
      }),
  });

  // Mutation pour activer/désactiver un utilisateur
  const toggleActiveMutation = useMutation({
    mutationFn: ({ userId, isActive }: { userId: string; isActive: boolean }) =>
      isActive
        ? userManagementApi.deactivateUser(userId)
        : userManagementApi.activateUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast.success("Statut de l'utilisateur modifié");
    },
    onError: (error: Error) => {
      toast.error(`Erreur: ${error.message}`);
    },
  });

  // Mutation pour supprimer un utilisateur
  const deleteUserMutation = useMutation({
    mutationFn: (userId: string) => userManagementApi.deleteUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast.success("Utilisateur supprimé");
    },
    onError: (error: Error) => {
      toast.error(`Erreur: ${error.message}`);
    },
  });

  const handleChangeRole = (user: { id: string; email: string; role: UserRole }) => {
    setSelectedUser(user);
    setIsRoleDialogOpen(true);
  };

  const handleToggleActive = (userId: string, isActive: boolean) => {
    toggleActiveMutation.mutate({ userId, isActive });
  };

  const handleDeleteUser = (userId: string, email: string) => {
    if (confirm(`Êtes-vous sûr de vouloir supprimer l'utilisateur ${email} ?`)) {
      deleteUserMutation.mutate(userId);
    }
  };

  // Filtrer les utilisateurs par recherche
  const filteredUsers = usersData?.filter((user) =>
    user.email.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  return (
    <RequireAuth roles={[UserRole.ADMIN]}>
      <div className="container mx-auto py-8 px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Gestion des utilisateurs</h1>
          <p className="text-gray-600">
            Gérez les utilisateurs, leurs rôles et leurs permissions
          </p>
        </div>

        {/* Barre de recherche et filtres */}
        <div className="flex gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Rechercher par email ou nom..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          <Select
            value={roleFilter}
            onValueChange={(value) => setRoleFilter(value as UserRole | "all")}
          >
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Filtrer par rôle" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous les rôles</SelectItem>
              {Object.entries(ROLE_LABELS).map(([role, label]) => (
                <SelectItem key={role} value={role}>
                  {label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Tableau des utilisateurs */}
        <div className="bg-white rounded-lg shadow">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Email</TableHead>
                  <TableHead>Rôle</TableHead>
                  <TableHead>Statut</TableHead>
                  <TableHead>Date d'inscription</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-8 text-gray-500">
                      Aucun utilisateur trouvé
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredUsers.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell className="font-medium">{user.email}</TableCell>
                      <TableCell>
                        <RoleBadge role={user.role} />
                      </TableCell>
                      <TableCell>
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${
                            user.is_active
                              ? "bg-green-100 text-green-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          {user.is_active ? "Actif" : "Inactif"}
                        </span>
                      </TableCell>
                      <TableCell>
                        {new Date(user.created_at).toLocaleDateString("fr-FR")}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleChangeRole(user)}
                          >
                            <Shield className="h-4 w-4 mr-1" />
                            Rôle
                          </Button>

                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleToggleActive(user.id, user.is_active)}
                          >
                            {user.is_active ? (
                              <>
                                <UserX className="h-4 w-4 mr-1" />
                                Désactiver
                              </>
                            ) : (
                              <>
                                <UserCheck className="h-4 w-4 mr-1" />
                                Activer
                              </>
                            )}
                          </Button>

                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleDeleteUser(user.id, user.email)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          )}
        </div>

        {/* Dialog de changement de rôle */}
        <ChangeRoleDialog
          isOpen={isRoleDialogOpen}
          onClose={() => {
            setIsRoleDialogOpen(false);
            setSelectedUser(null);
          }}
          user={selectedUser}
        />
      </div>
    </RequireAuth>
  );
}
