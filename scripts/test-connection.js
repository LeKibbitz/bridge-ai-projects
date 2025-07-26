const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function testConnection() {
  try {
    console.log('🔍 Test de connexion à la base de données...');
    
    // Test de connexion simple
    await prisma.$connect();
    console.log('✅ Connexion réussie !');
    
    // Compter les clubs
    const clubCount = await prisma.club.count();
    console.log(`📊 Nombre de clubs dans la base : ${clubCount}`);
    
    // Compter les joueurs
    const playerCount = await prisma.joueur.count();
    console.log(`👥 Nombre de joueurs dans la base : ${playerCount}`);
    
    // Afficher quelques clubs
    if (clubCount > 0) {
      console.log('\n🏢 Clubs dans la base :');
      const clubs = await prisma.club.findMany({
        take: 5,
        select: {
          id: true,
          nom: true,
          code: true,
          email: true,
        }
      });
      
      clubs.forEach(club => {
        console.log(`  - ${club.nom} (${club.code}) - ${club.email || 'Pas d\'email'}`);
      });
    }
    
    // Afficher quelques joueurs
    if (playerCount > 0) {
      console.log('\n👤 Joueurs dans la base :');
      const players = await prisma.joueur.findMany({
        take: 5,
        include: {
          club: {
            select: {
              nom: true,
              code: true,
            }
          }
        }
      });
      
      players.forEach(player => {
        console.log(`  - ${player.prenom} ${player.nom} (${player.licence}) - Club: ${player.club?.nom || 'Inconnu'}`);
      });
    }
    
  } catch (error) {
    console.error('❌ Erreur de connexion :', error.message);
  } finally {
    await prisma.$disconnect();
  }
}

testConnection(); 