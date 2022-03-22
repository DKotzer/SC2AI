from re import U
from sc2.bot_ai import BotAI # parent AI class that you will inherit from
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2 import maps
from sc2.ids.unit_typeid import UnitTypeId
import random


class DylanBot(BotAI):
    async def on_step(self, iteration:int):

        print(f"This is my bot in iteration {iteration}, workers: {self.workers}, idle workers: {self.workers.idle}, supply: {self.supply_used}/{self.supply_cap}")
        print(f"{iteration}, n_workers: {self.workers.amount}, n_idle_workers: {self.workers.idle.amount},", \
        f"minerals: {self.minerals}, gas: {self.vespene}, cannons: {self.structures(UnitTypeId.PHOTONCANNON).amount},", \
        f"pylons: {self.structures(UnitTypeId.PYLON).amount}, nexus: {self.structures(UnitTypeId.NEXUS).amount}", \
        f"gateways: {self.structures(UnitTypeId.GATEWAY).amount}, cybernetics cores: {self.structures(UnitTypeId.CYBERNETICSCORE).amount}", \
        f"stargates: {self.structures(UnitTypeId.STARGATE).amount}, voidrays: {self.units(UnitTypeId.VOIDRAY).amount}, supply: {self.supply_used}/{self.supply_cap}")


        await self.distribute_workers()

        if self.townhalls:
            nexus = self.townhalls.random
            ramp = self.main_base_ramp
            
            if nexus.is_idle and self.can_afford(UnitTypeId.PROBE):
                nexus.train(UnitTypeId.PROBE)
        
            elif not self.structures(UnitTypeId.PYLON) and self.already_pending(UnitTypeId.PYLON) == 0:
                if self.can_afford(UnitTypeId.PYLON):
                    await self.build(UnitTypeId.PYLON, near=nexus) #look in to other options in documentation


            elif self.structures(UnitTypeId.PYLON).amount < 2:
                if self.can_afford(UnitTypeId.PYLON):
                    await self.build(UnitTypeId.PYLON, near=nexus)

            elif self.structures(UnitTypeId.PYLON).amount < 4:
                if self.can_afford(UnitTypeId.PYLON):
                    await self.build(UnitTypeId.PYLON, near=ramp.protoss_wall_pylon)    

            elif self.structures(UnitTypeId.PYLON).amount < 7:
                if self.can_afford(UnitTypeId.PYLON):
                    target_pylon = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])
                    
                    pos = target_pylon.position.towards(self.enemy_start_locations[0], random.randrange(8,15))
                    await self.build(UnitTypeId.PYLON, near=pos)

            elif not self.structures(UnitTypeId.FORGE):
                if self.can_afford(UnitTypeId.FORGE):
                    await self.build(UnitTypeId.FORGE, near= self.structures(UnitTypeId.PYLON).closest_to(nexus))

            elif self.structures(UnitTypeId.FORGE).ready and self.structures(UnitTypeId.PHOTONCANNON).amount < 5:
                if self.can_afford(UnitTypeId.PHOTONCANNON):
                    await self.build(UnitTypeId.PHOTONCANNON, near= self.structures(UnitTypeId.PYLON).closest_to(ramp.protoss_wall_pylon))


        else:
            if self.can_afford(UnitTypeId.NEXUS):
                await self.expand_now()

run_game(
    maps.get("2000AtmospheresAIE"),
    [Bot(Race.Protoss, DylanBot()),
    Computer(Race.Zerg, Difficulty.Hard)],
    realtime=False
)