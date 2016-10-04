# -*- coding: utf-8 -*-
##############################################################################
#
#   Discounts and Coupons
#   Authors: Dominador B. Ramos Jr. <mongramosjr@gmail.com>
#   Company: 3D2N World (http://www.3d2nworld.com)
#
#   Copyright 2016 Dominador B. Ramos Jr.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
##############################################################################

import openerp
from openerp import tools


def deal_image_resize_image_banner(base64_source, size=(1280, 960), encoding='base64', filetype=None, avoid_if_small=True):
    return tools.image_resize_image(base64_source, size, encoding, filetype, avoid_if_small)
    
def deal_image_resize_image_icon(base64_source, size=(128, 128), encoding='base64', filetype=None, avoid_if_small=True):
    return tools.image_resize_image(base64_source, size, encoding, filetype, avoid_if_small)
    
    
def deal_image_resize_image_wide(base64_source, size=(1280, 720), encoding='base64', filetype=None, avoid_if_small=True):
    return tools.image_resize_image(base64_source, size, encoding, filetype, avoid_if_small)


def deal_image_get_resized_images(base64_source, return_banner=False, return_icon=True, return_wide=True,
    banner_name='image', icon_name='image_icon', wide_name='image_wide',
    avoid_resize_banner=True, avoid_resize_icon=True, avoid_resize_wide=True):

    deal_image_dict = dict()
    if return_banner:
        deal_image_dict[banner_name] = deal_image_resize_image_banner(base64_source, avoid_if_small=avoid_resize_banner)
    if return_icon:
        deal_image_dict[icon_name] = deal_image_resize_image_icon(base64_source, avoid_if_small=avoid_resize_icon)
    if return_wide:
        deal_image_dict[wide_name] = deal_image_resize_image_wide(base64_source, avoid_if_small=avoid_resize_wide)
    return deal_image_dict
    

def deal_image_resize_images(vals, banner_name='image', icon_name='image_icon', wide_name='image_wide'):
    """ Update ``vals`` with image fields resized as expected. """
    if banner_name in vals:
        vals.update(deal_image_get_resized_images(vals[banner_name],
                        return_banner=True, return_icon=True, return_wide=True,
                        banner_name=banner_name, icon_name=icon_name, wide_name=wide_name,
                        avoid_resize_banner=True, avoid_resize_icon=True, avoid_resize_wide=True))
                        
    elif wide_name in vals:
        vals.update(deal_image_get_resized_images(vals[wide_name],
                        return_banner=True, return_icon=True, return_wide=True,
                        banner_name=banner_name, icon_name=icon_name, wide_name=wide_name,
                        avoid_resize_banner=True, avoid_resize_icon=True, avoid_resize_wide=True))
                         
    elif icon_name in vals:
        vals.update(deal_image_get_resized_images(vals[icon_name],
                        return_banner=True, return_icon=True, return_wide=True,
                        banner_name=banner_name, icon_name=icon_name, wide_name=wide_name,
                        avoid_resize_banner=True, avoid_resize_icon=True, avoid_resize_wide=True))


