import math
import torch
from torch import nn

N = 2
c_in = 8
c = 10
N_head = 4
attn_dim = -3
d1 = 3
d2 = 5
d_attn = 6
d4 = 7
T = 9
hidden_size = 11
intermediate_size = 12

feature_shapes = {
    'q': (d1, d2,d_attn, d4, N_head*c),
    'k': (d1, d2, d_attn, d4, N_head*c),
    'v': (d1, d2, d_attn, d4, N_head*c),
    'q_global': (d1, d2,d_attn, d4, N_head*c),
    'k_global': (d1, d2, d_attn, d4, c),
    'v_global': (d1, d2, d_attn, d4, c),
    'x': (d1, d2, d_attn, d4, c_in),
    'bias': (N_head, d_attn, d_attn),
    'fake_attention_mask': (d1, d2, d4, d_attn),
    'sentiment_attn_input': (N, T, hidden_size),
    'sentiment_attn_mask': (N, T),
    'input_ids': (128,),
    'attention_mask': (128,),
    'label': tuple(),
}

batched_feature_shapes = {
    key: (N,) + value
    for key, value in feature_shapes.items()
}

test_inputs = {
    key: torch.linspace(-2-i/5, 2+i/5, math.prod(shape)).reshape(shape).double()
    for i, (key, shape) in enumerate(feature_shapes.items())
}

test_inputs['fake_attention_mask'] = torch.ones((d1, d2, d4, d_attn))
test_inputs['fake_attention_mask'][..., 2:4] = 0
test_inputs['sentiment_attn_mask'] = torch.ones((N, T))
test_inputs['sentiment_attn_mask'][1, 3:5] = 0

test_inputs['input_ids'] = torch.tensor([  101,  5342,  2047,  3595,  8496,  2013,  1996, 18643,  3197,   102,
            0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
            0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
            0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
            0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
            0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
            0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
            0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
            0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
            0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
            0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
            0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
            0,     0,     0,     0,     0,     0,     0,     0])

test_inputs['attention_mask'] = torch.tensor([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0])

test_inputs['sentiment_full_input'] = {
    'input_ids': test_inputs['input_ids'],
    'attention_mask': test_inputs['attention_mask'],
    'label': torch.tensor(0),
}


# test_inputs['residue_index'] = torch.arange(N_res).view(N_res, 1).broadcast_to(N_res, N_cycle)
# test_inputs['target_feat'] = nn.functional.one_hot(torch.arange(N_res)%20, num_classes=tf_dim).double()
# test_inputs['target_feat'] = test_inputs['target_feat'].unsqueeze(-1).broadcast_to(feature_shapes['target_feat'])
# 
# test_inputs['batch'] = {
#     'msa_feat': test_inputs['msa_feat'],
#     'target_feat': test_inputs['target_feat'],
#     'residue_index': test_inputs['residue_index'],
#     'extra_msa_feat': test_inputs['extra_msa_feat'],
# }

def test_module_shape(module, test_name, control_folder, overwrite_results=False):
    param_shapes = {name: param.shape for name, param in module.named_parameters()}

    shapes_path = f'{control_folder}/{test_name}_param_shapes.pt'

    if overwrite_results:
        torch.save(param_shapes, shapes_path)

    expected_shapes = torch.load(shapes_path)

    keys_in_dict1_only = set(param_shapes.keys()) - set(expected_shapes.keys())
    keys_in_dict2_only = set(expected_shapes.keys()) - set(param_shapes.keys())

    if keys_in_dict1_only or keys_in_dict2_only:
        error_message = "Parameter key set mismatch:\n"
        if keys_in_dict1_only:
            error_message += f"Unexpected keys: {keys_in_dict1_only}\n"
        if keys_in_dict2_only:
            error_message += f"Missing keys: {keys_in_dict2_only}\n"
        raise AssertionError(error_message)

    for name, param_shape in param_shapes.items():
        assert param_shape == expected_shapes[name], f'Invalid shape for parameter {name}.'
            

    
def controlled_execution(module, inp, method):
    was_training = module.training
    module.eval()
    module.double()
    with torch.no_grad():
        original_params = [param.clone() for param in module.parameters()]
        for param in module.parameters():
            param.copy_(torch.linspace(-1, 1, param.numel()).reshape(param.shape))

        out = method(*inp)

        for orig_param, param in zip(original_params, module.parameters()):
            param.copy_(orig_param)

    if was_training:
        module.train()

    return out

def controlled_forward(module, inp):
    return controlled_execution(module, inp, lambda *x: module(*x))
    

def test_module_method(module, test_name, input_names, output_names, control_folder, method, include_batched=True, overwrite_results=False):
    if not isinstance(input_names, (tuple, list)):
        input_names = (input_names,)

    if not isinstance(output_names, (tuple, list)):
        output_names = (output_names,)

    non_batched_inps = tuple(test_inputs[name] for name in input_names)

    if include_batched: 
        batched_inps = []
        for name in input_names:
            inp = test_inputs[name]
            if isinstance(inp, dict):
                batched_inp = {
                    key: value.broadcast_to(batched_feature_shapes[key])
                    for key, value in inp.items()
                }
            else:
                batched_inp = inp.broadcast_to(batched_feature_shapes[name])
            batched_inps.append(batched_inp)

        batched_inp = tuple(batched_inp)

    with torch.no_grad():
        non_batched_out = controlled_execution(module, non_batched_inps, method)
        if include_batched:
            batched_out = controlled_execution(module, batched_inps, method)

    if not isinstance(non_batched_out, (tuple, list)):
        non_batched_out = (non_batched_out,)
        if include_batched:
            batched_out = (batched_out,)

    out_file_names = [f'{control_folder}/{test_name}_{out_name}.pt' for out_name in output_names]

    if overwrite_results:
        for out, out_name in zip(non_batched_out, out_file_names):
            torch.save(out, out_name)

    for out, out_file_name, out_name in zip(non_batched_out, out_file_names, output_names):
        expected_out = torch.load(out_file_name)
        assert torch.allclose(out, expected_out), f'Problem with output {out_name} in test {test_name} in non-batched check.'

    if include_batched:
        for out, out_file_name, out_name in zip(batched_out, out_file_names, output_names):
            expected_out = torch.load(out_file_name)
            expected_out_batch_shape = (N,) + expected_out.shape
            expected_out = expected_out.unsqueeze(0).broadcast_to(expected_out_batch_shape)

            max_abs_err = (out.double()-expected_out.double()).abs().max()
            max_rel_err = ((out.double()-expected_out.double()).abs() / (torch.maximum(out.double().abs(), expected_out.double().abs())+1e-8)).max()
            # print(f'Max batched error: abs {max_abs_err}; rel {max_rel_err}')

            assert torch.allclose(out, expected_out), f'Problem with output {out_name} in test {test_name} in batched check. Maximum absolute error: {max_abs_err}. Maximum relative error: {max_rel_err}.'

    
def test_module_forward(module, test_name, input_names, output_names, control_folder, overwrite_results=False):
    test_module_method(module, test_name, input_names, output_names, control_folder, lambda *x: module(*x), overwrite_results=overwrite_results)


