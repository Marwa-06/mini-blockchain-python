import hashlib
import time
from typing import List

# -------------------------
# Classe Block
# -------------------------
class Block:
    def __init__(self, index: int, timestamp: float, data: str, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        
        #Calcule le SHA-256 du bloc selon les champs demandés :
        # index + timestamp + data + previous_hash + nonce
        
        block_string = (
            str(self.index)
            + str(self.timestamp)
            + str(self.data)
            + str(self.previous_hash)
            + str(self.nonce)
        )
        return hashlib.sha256(block_string.encode()).hexdigest()

    def __repr__(self) -> str:
        return (
            f"Block(index={self.index}, timestamp={self.timestamp}, "
            f"data={self.data!r}, previous_hash={self.previous_hash[:10]}..., "
            f"nonce={self.nonce}, hash={self.hash[:10]}...)"
        )

# -------------------------
# Classe Blockchain
# -------------------------
class Blockchain:
    def __init__(self, difficulty: int = 2):
        # IMPORTANT : définir difficulty AVANT create_genesis_block()
        self.difficulty = difficulty
        self.chain: List[Block] = [self.create_genesis_block()]


    def create_genesis_block(self) -> Block:
        #Crée et retourne le bloc genesis (index 0)
        genesis = Block(0, time.time(), "Genesis Block", "0")
        # pour que genesis respecte la difficulté, on peut miner (optionnel)
        genesis = self.proof_of_work(genesis)
        return genesis

    def get_last_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, data: str) -> Block:
        
        #Crée un bloc avec les données fournies, effectue le minage (PoW),
        #l'ajoute à la chaîne et retourne le bloc miné
        
        last = self.get_last_block()
        new_block = Block(len(self.chain), time.time(), data, last.hash)
        mined = self.proof_of_work(new_block)
        self.chain.append(mined)
        return mined

    def proof_of_work(self, block: Block) -> Block:
        
        #Incrémente block.nonce jusqu'à obtenir un hash qui commence par le préfixe 
        # '0' * difficulty. Affiche infos de minage (nonce, temps).
        
        prefix = "0" * self.difficulty
        start = time.time()
        attempts = 0

        while True:
            block.hash = block.calculate_hash()
            if block.hash.startswith(prefix):
                elapsed = time.time() - start
                print(
                    f"Miné : index={block.index} nonce={block.nonce} hash={block.hash} "
                    f"(temps={elapsed:.3f}s, essais={attempts})"
                )
                return block
            block.nonce += 1
            attempts += 1

    def is_chain_valid(self) -> bool:
        
        prefix = "0" * self.difficulty

        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Vérifier previous_hash
            if current.previous_hash != previous.hash:
                print(f"Invalid: block {i} previous_hash mismatch")
                return False

            # Recalculer le hash à partir des champs (y compris nonce)
            recalculated_hash = current.calculate_hash()
            if current.hash != recalculated_hash:
                print(f"Invalid: block {i} hash mismatch (stored != recalculated)")
                return False

            # Vérifier la difficulté
            if not current.hash.startswith(prefix):
                print(f"Invalid: block {i} does not satisfy difficulty (prefix {prefix})")
                return False

        return True

    def tamper_with_block(self, index: int, new_data: str):
        
        if index <= 0 or index >= len(self.chain):
            raise IndexError("Impossible de modifier ce bloc (index hors limites ou genesis).")
        self.chain[index].data = new_data
        # Mettre à jour le hash pour refléter la modification sans minage (simulate temping)
        self.chain[index].hash = self.chain[index].calculate_hash()

    def print_chain(self):
        for b in self.chain:
            print("--- Bloc", b.index, "---")
            print("Horodatage :", b.timestamp)
            print("Données :", b.data)
            print("Nonce :", b.nonce)
            print("Hash :", b.hash)
            print("Hash précédent :", b.previous_hash)
            print()


# Programme principal / démonstration

if __name__ == "__main__":
    
    difficulty = 3  
    print(f"Initialisation de la blockchain (difficulty={difficulty})...\n")
    bc = Blockchain(difficulty=difficulty)

    # Ajout de blocs (minage)
    bc.add_block("Transaction : Alice -> Bob")
    bc.add_block("Transaction : Bob -> Charlie")
    bc.add_block("Transaction : Charlie -> David")

    print("\n--- Chaîne complète après minage ---")
    bc.print_chain()

    # Vérifier validité
    print("Vérification de la blockchain :", bc.is_chain_valid())

    # Tamper (pour le rapport : montrer invalidation)
    print("\n--- Tampering : modification du bloc 2 (sans re-miner) ---")
    bc.tamper_with_block(2, "Transaction : Bob -> Eve (MODIFIE)")
    bc.print_chain()
    print("Vérification après modification (doit être False) :", bc.is_chain_valid())

