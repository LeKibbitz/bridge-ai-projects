const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const csv = require('csv-parser');

const prisma = new PrismaClient();

// Fonction pour nettoyer et filtrer les rôles/fonctions/agréments
function cleanAndFilterItems(itemsString, excludedItems = ['Joueur', 'Joueuse', 'Capitaine']) {
  if (!itemsString) return [];
  
  return itemsString
    .split(';')
    .map(item => item.trim())
    .filter(item => item && !excludedItems.includes(item));
}

// Fonction pour créer ou récupérer un rôle
async function getOrCreateRole(nom) {
  return await prisma.role.upsert({
    where: { nom },
    update: {},
    create: { nom }
  });
}

// Fonction pour créer ou récupérer une fonction
async function getOrCreateFunction(nom) {
  return await prisma.function.upsert({
    where: { nom },
    update: {},
    create: { nom }
  });
}

// Fonction pour créer ou récupérer un agrément
async function getOrCreateAgrement(nom) {
  return await prisma.agrement.upsert({
    where: { nom },
    update: {},
    create: { nom }
  });
}

async function importClubs() {
  console.log('🔄 Import des clubs...');
  
  const clubs = [];
  
  return new Promise((resolve, reject) => {
    fs.createReadStream('../clubs.csv')
      .pipe(csv())
      .on('data', (row) => {
        // Mapper les colonnes CSV vers notre modèle Prisma
        const club = {
          code: row.club_code,
          nom: row.club_name,
          adresse: row.info_text_2 || null,
          telephone: row.phone_main || null,
          email: row.email || null,
          site_web: row.website || null,
        };
        clubs.push(club);
      })
      .on('end', async () => {
        try {
          for (const club of clubs) {
            await prisma.club.upsert({
              where: { code: club.code },
              update: club,
              create: club,
            });
          }
          console.log(`✅ ${clubs.length} clubs importés avec succès`);
          resolve();
        } catch (error) {
          console.error('❌ Erreur lors de l\'import des clubs:', error);
          reject(error);
        }
      });
  });
}

async function importPlayers() {
  console.log('🔄 Import des joueurs...');
  
  const players = [];
  
  return new Promise((resolve, reject) => {
    fs.createReadStream('../players.csv')
      .pipe(csv())
      .on('data', (row) => {
        // Mapper les colonnes CSV vers notre modèle Prisma
        const player = {
          licence: row.licence_number,
          nom: row.last_name,
          prenom: row.first_name,
          date_naissance: row.birthdate ? new Date(row.birthdate) : null,
          email: null, // Pas dans le CSV
          telephone: null, // Pas dans le CSV
          club_id: null, // Sera mis à jour après avoir trouvé le club
          club_code: row.club_code, // Temporaire pour la liaison
          
          // Données pour les relations
          roles: cleanAndFilterItems(row.roles),
          functions: cleanAndFilterItems(row.functions),
          agrements: cleanAndFilterItems(row.agrements),
        };
        players.push(player);
      })
      .on('end', async () => {
        try {
          for (const player of players) {
            // Trouver le club par son code
            const club = await prisma.club.findUnique({
              where: { code: player.club_code }
            });
            
            if (club) {
              const { club_code, roles, functions, agrements, ...playerData } = player;
              playerData.club_id = club.id;
              
              // Créer ou mettre à jour le joueur
              const createdPlayer = await prisma.joueur.upsert({
                where: { licence: player.licence },
                update: playerData,
                create: playerData,
              });
              
              // Gérer les rôles
              for (const roleNom of roles) {
                const role = await getOrCreateRole(roleNom);
                await prisma.joueurRole.upsert({
                  where: {
                    joueur_id_role_id: {
                      joueur_id: createdPlayer.id,
                      role_id: role.id
                    }
                  },
                  update: {},
                  create: {
                    joueur_id: createdPlayer.id,
                    role_id: role.id
                  }
                });
              }
              
              // Gérer les fonctions
              for (const functionNom of functions) {
                const func = await getOrCreateFunction(functionNom);
                await prisma.joueurFunction.upsert({
                  where: {
                    joueur_id_function_id: {
                      joueur_id: createdPlayer.id,
                      function_id: func.id
                    }
                  },
                  update: {},
                  create: {
                    joueur_id: createdPlayer.id,
                    function_id: func.id
                  }
                });
              }
              
              // Gérer les agréments
              for (const agrementNom of agrements) {
                const agrement = await getOrCreateAgrement(agrementNom);
                await prisma.joueurAgrement.upsert({
                  where: {
                    joueur_id_agrement_id: {
                      joueur_id: createdPlayer.id,
                      agrement_id: agrement.id
                    }
                  },
                  update: {},
                  create: {
                    joueur_id: createdPlayer.id,
                    agrement_id: agrement.id
                  }
                });
              }
              
            } else {
              console.warn(`⚠️ Club non trouvé pour le joueur ${player.licence} (code: ${player.club_code})`);
            }
          }
          console.log(`✅ ${players.length} joueurs importés avec succès`);
          resolve();
        } catch (error) {
          console.error('❌ Erreur lors de l\'import des joueurs:', error);
          reject(error);
        }
      });
  });
}

async function main() {
  try {
    console.log('🚀 Début de l\'import des données...');
    
    await importClubs();
    await importPlayers();
    
    console.log('🎉 Import terminé avec succès !');
  } catch (error) {
    console.error('💥 Erreur lors de l\'import:', error);
  } finally {
    await prisma.$disconnect();
  }
}

main(); 