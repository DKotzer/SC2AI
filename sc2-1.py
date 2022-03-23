
from sc2.bot_ai import BotAI # parent AI class that you will inherit from
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2 import maps
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.buff_id import BuffId
from sc2.constants import *
import random

class DylanBot(BotAI):
    def __init__(self):
        self.raw_affects_selection = True
    async def on_step(self, iteration:int):
        print(f"This is iteration {iteration}")

        # print(f"This is my bot in iteration {iteration}, workers: {self.workers}, idle workers: {self.workers.idle}, supply: {self.supply_used}/{self.supply_cap}")
        # print(f"{iteration}, n_workers: {self.workers.amount}, n_idle_workers: {self.workers.idle.amount},", \
        # f"minerals: {self.minerals}, gas: {self.vespene}, cannons: {self.structures(UnitTypeId.PHOTONCANNON).amount},", \
        # f"pylons: {self.structures(UnitTypeId.PYLON).amount}, nexus: {self.structures(UnitTypeId.NEXUS).amount}", \
        # f"gateways: {self.structures(UnitTypeId.GATEWAY).amount}, cybernetics cores: {self.structures(UnitTypeId.CYBERNETICSCORE).amount}", \
        # f"stargates: {self.structures(UnitTypeId.STARGATE).amount}, voidrays: {self.units(UnitTypeId.VOIDRAY).amount}, supply: {self.supply_used}/{self.supply_cap}")

        await self.distribute_workers()

        if iteration == 0:
            await self.chat_send("GL HF")

        if self.townhalls:

            # nexus = self.townhalls.random
            nexus = self.townhalls.ready.random
            ramp = self.main_base_ramp

            if self.structures(UnitTypeId.VOIDRAY).amount < 18 and self.can_afford(UnitTypeId.VOIDRAY):
                for sg in self.structures(UnitTypeId.STARGATE).ready.idle:
                    sg.train(UnitTypeId.VOIDRAY)
            
            supply_remaining = self.supply_cap - self.supply_used
            # Attack with all workers if we don't have any nexuses left, attack-move on enemy spawn (doesn't work on 4 player map) so that probes auto attack on the way
                        
            if not nexus.is_idle and not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                nexuses = self.structures(UnitTypeId.NEXUS)
                abilities = await self.get_available_abilities(nexuses)
                for loop_nexus, abilities_nexus in zip(nexuses, abilities):
                    if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities_nexus:
                        loop_nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)
                        break

            if self.supply_workers + self.already_pending(UnitTypeId.PROBE) < self.townhalls.amount * 22 and nexus.is_idle:
                if self.can_afford(UnitTypeId.PROBE):
                    nexus.train(UnitTypeId.PROBE)
        
            elif not self.structures(UnitTypeId.PYLON) and self.already_pending(UnitTypeId.PYLON) == 0:
                if self.can_afford(UnitTypeId.PYLON):
                    await self.build(UnitTypeId.PYLON, near=nexus) #look in to other options in documentation

            elif self.structures(UnitTypeId.PYLON).amount <= 2 and self.supply_left < 4 and self.already_pending(UnitTypeId.PYLON) < 2:
                if self.can_afford(UnitTypeId.PYLON):
                    await self.build(UnitTypeId.PYLON, near=ramp.protoss_wall_pylon)
            
            # elif self.structures(UnitTypeId.PYLON).amount < 5:
            #     if self.can_afford(UnitTypeId.PYLON):
            #         await self.build(UnitTypeId.PYLON, near=nexus)

            elif self.structures(UnitTypeId.PYLON).amount < 20 and self.supply_used > 15 and self.supply_left < 4 and self.already_pending(UnitTypeId.PYLON) < 2:
                if self.can_afford(UnitTypeId.PYLON):
                    # target_pylon = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])
                    
                    # pos = target_pylon.position.towards(self.enemy_start_locations[0], random.randrange(8,15))
                    await self.build(UnitTypeId.PYLON, near=nexus.position.towards(self.game_info.map_center, 5))



            # buildings = [UnitTypeId.GATEWAY, UnitTypeId.CYBERNETICSCORE,UnitTypeId.STARGATE] #how to continue the elif after this? maybe make a global variable game-phase, set to mid game after stargate built and then a new if for midgame, bad idea though because we need to earlier logic too
            # #loop through buildings and build one if one does not exist and is not already building
            # for building in buildings:
            #     if not self.structures(building):
            #         if self.can_afford(building) and self.already_pending(building)==0:
            #             await self.build(building,near= nexus)
            #             # await self.build(building,near= self.structures(UnitTypeId.PYLON).closest_to(nexus))
            #         break

            
             # a gateway? this gets us towards cyb core > stargate > void ray
            elif not self.structures(UnitTypeId.GATEWAY):
                if self.can_afford(UnitTypeId.GATEWAY):
                    await self.build(UnitTypeId.GATEWAY, near=self.structures(UnitTypeId.PYLON).closest_to(self.townhalls.random))
            
            # a cyber core? this gets us towards stargate > void ray
            elif not self.structures(UnitTypeId.CYBERNETICSCORE):
                if self.can_afford(UnitTypeId.CYBERNETICSCORE):
                    await self.build(UnitTypeId.CYBERNETICSCORE, near=self.structures(UnitTypeId.PYLON).closest_to(self.townhalls.random))

            elif not self.structures(UnitTypeId.FORGE):
                if self.can_afford(UnitTypeId.FORGE):
                    await self.build(UnitTypeId.FORGE, near= self.structures(UnitTypeId.PYLON).closest_to(self.townhalls.random))

            elif self.structures(UnitTypeId.FORGE).ready and self.structures(UnitTypeId.PHOTONCANNON).amount < 3:
                if self.can_afford(UnitTypeId.PHOTONCANNON):
                    await self.build(UnitTypeId.PHOTONCANNON, ramp.protoss_wall_buildings[0])
            

            # a stargate? this gets us towards void ray
            elif self.structures(UnitTypeId.STARGATE).amount <=2 and self.already_pending(UnitTypeId.STARGATE) == 0:
                if self.can_afford(UnitTypeId.STARGATE):
                    await self.build(UnitTypeId.STARGATE, near=self.structures(UnitTypeId.PYLON).closest_to(self.townhalls.random))
            
            
            if self.structures(UnitTypeId.CYBERNETICSCORE):
                for nexus in self.townhalls.ready:
                    vespenes = self.vespene_geyser.closer_than(15, nexus)
                    for vg in vespenes:
                        if not self.gas_buildings or not self.gas_buildings.closer_than(1, vg) and self.can_afford(UnitTypeId.ASSIMILATOR):
                            await self.build(UnitTypeId.ASSIMILATOR, vg)


            
            if self.townhalls.ready.amount + self.already_pending(UnitTypeId.NEXUS) < 3:
                if self.can_afford(UnitTypeId.NEXUS):
                    await self.expand_now()
            
            elif self.minerals > 1000:
                await self.build(UnitTypeId.PHOTONCANNON, near= nexus.position.towards(self.game_info.map_center, 5))

            # elif self.structures(UnitTypeId.FORGE).ready and self.structures(UnitTypeId.PHOTONCANNON).amount < 6:
            #     if self.can_afford(UnitTypeId.PHOTONCANNON):
            #         await self.build(UnitTypeId.PHOTONCANNON, near= self.structures(UnitTypeId.PYLON).closest_to(ramp.protoss_wall_pylon)) 
            

        else:
            if self.can_afford(UnitTypeId.NEXUS):
                await self.expand_now()
        
        ## Attack logic
        for vr in self.units(UnitTypeId.VOIDRAY):
            abilities = await self.get_available_abilities(vr)
            if AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT in abilities:
                vr(AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT)


        #             if vr.weapon_cooldown == 0:
        #                 vr(AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT)

        if self.units(UnitTypeId.VOIDRAY).amount >= 15:
            
            if self.enemy_units:
                for vr in self.units(UnitTypeId.VOIDRAY):
                    vr.attack((self.enemy_units).closest_to(vr))
            
            elif self.enemy_structures:
                for vr in self.units(UnitTypeId.VOIDRAY):
                    # if vr.weapon_cooldown > 0:
                    #     vr(AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT)
                    vr.attack((self.enemy_structures).closest_to(vr))
                
            else:
                for vr in self.units(UnitTypeId.VOIDRAY):
                    # if vr.weapon_cooldown > 0:
                    #     vr(AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT)
                    vr.attack(self.enemy_start_locations[0]) # change this to enemey_start_locations[random range(len(enemy_start_locations))] - write the range part properly
                
            
run_game(
    maps.get("2000AtmospheresAIE"),
    [Bot(Race.Protoss, DylanBot()),
    Computer(Race.Zerg, Difficulty.VeryHard)],
    realtime=False
)